#!/usr/bin/env python3
"""Pull small volatility-index and event-calendar context datasets.

All source responses are retained where practical. Normalized Parquet outputs
are written atomically and may be regenerated safely.
"""

from __future__ import annotations

import calendar
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import exchange_calendars as xcals
import httpx
import pandas as pd
import polars as pl
import yfinance as yf
from bs4 import BeautifulSoup
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "data" / "external-context"
RAW_ROOT = OUTPUT_ROOT / "raw"
NORMALIZED_ROOT = OUTPUT_ROOT / "normalized"
MANIFEST_ROOT = ROOT / "manifests"
NY = ZoneInfo("America/New_York")
START_DATE = date(2010, 1, 1)
END_DATE = date.today().replace(year=date.today().year + 2)

FRED_SERIES = {
    "VIXCLS": "VIX",
    "VXNCLS": "VXN",
    "VXVCLS": "VIX3M",
}
FRED_RELEASES = {
    10: ("cpi", "Consumer Price Index", time(8, 30)),
    50: ("nfp", "Employment Situation", time(8, 30)),
}
MEGA_CAP_SYMBOLS = (
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "AVGO",
    "BRK-B",
    "JPM",
    "LLY",
    "WMT",
    "ORCL",
    "V",
    "MA",
    "XOM",
    "NFLX",
    "COST",
    "AMD",
    "HD",
)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    partial.write_text(text, encoding="utf-8")
    os.replace(partial, path)


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    partial.write_bytes(payload)
    os.replace(partial, path)


def atomic_parquet(frame: pl.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    frame.write_parquet(
        partial,
        compression="zstd",
        compression_level=3,
        statistics=True,
    )
    os.replace(partial, path)


def fred_get(client: httpx.Client, endpoint: str, **params: object) -> dict:
    api_key = os.environ["FRED_API_KEY"]
    response = client.get(
        f"https://api.stlouisfed.org/fred/{endpoint}",
        params={"api_key": api_key, "file_type": "json", **params},
    )
    response.raise_for_status()
    return response.json()


def fetch_fred_volatility(client: httpx.Client) -> tuple[list[dict], dict]:
    summary: dict[str, dict] = {}
    all_rows: list[dict] = []
    for series_id, symbol in FRED_SERIES.items():
        info = fred_get(client, "series", series_id=series_id)
        payload = fred_get(
            client,
            "series/observations",
            series_id=series_id,
            observation_start="1990-01-01",
            observation_end=END_DATE.isoformat(),
        )
        atomic_text(
            RAW_ROOT / "fred" / f"{series_id}.json",
            json.dumps({"series": info, "observations": payload}, indent=2) + "\n",
        )
        rows = []
        for item in payload["observations"]:
            value = None if item["value"] == "." else float(item["value"])
            rows.append(
                {
                    "date": date.fromisoformat(item["date"]),
                    "symbol": symbol,
                    "series_id": series_id,
                    "value": value,
                    "realtime_start": date.fromisoformat(item["realtime_start"]),
                    "realtime_end": date.fromisoformat(item["realtime_end"]),
                    "source": "FRED",
                }
            )
        frame = pl.DataFrame(rows).sort("date")
        atomic_parquet(frame, NORMALIZED_ROOT / "volatility" / f"{symbol}.parquet")
        all_rows.extend(rows)
        valid = frame.filter(pl.col("value").is_not_null())
        summary[symbol] = {
            "rows": frame.height,
            "valid_rows": valid.height,
            "start": str(valid["date"].min()),
            "end": str(valid["date"].max()),
        }
    atomic_parquet(
        pl.DataFrame(all_rows).sort(["symbol", "date"]),
        NORMALIZED_ROOT / "volatility" / "fred-volatility.parquet",
    )
    return all_rows, summary


def fetch_vvix(client: httpx.Client) -> dict:
    url = "https://cdn.cboe.com/api/global/us_indices/daily_prices/VVIX_History.csv"
    response = client.get(url)
    response.raise_for_status()
    atomic_bytes(RAW_ROOT / "cboe" / "VVIX_History.csv", response.content)
    frame = pl.read_csv(response.content).rename({"DATE": "date", "VVIX": "value"})
    frame = frame.with_columns(
        pl.col("date").str.to_date("%m/%d/%Y"),
        pl.lit("VVIX").alias("symbol"),
        pl.lit("Cboe").alias("source"),
    ).select("date", "symbol", "value", "source").sort("date")
    atomic_parquet(frame, NORMALIZED_ROOT / "volatility" / "VVIX.parquet")
    return {
        "rows": frame.height,
        "start": str(frame["date"].min()),
        "end": str(frame["date"].max()),
    }


def event_row(
    *,
    event_date: date,
    event_type: str,
    event_name: str,
    source: str,
    source_url: str,
    symbol: str | None = None,
    event_ts_utc: datetime | None = None,
    event_time_et: str | None = None,
    status: str = "scheduled_or_observed",
    time_basis: str = "date_only",
    details: dict | None = None,
) -> dict:
    return {
        "event_date": event_date,
        "event_ts_utc": event_ts_utc,
        "event_time_et": event_time_et,
        "event_type": event_type,
        "event_name": event_name,
        "symbol": symbol,
        "status": status,
        "time_basis": time_basis,
        "source": source,
        "source_url": source_url,
        "details_json": json.dumps(details or {}, sort_keys=True),
    }


def fetch_fred_release_calendars(client: httpx.Client) -> tuple[list[dict], dict]:
    events: list[dict] = []
    summary: dict[str, int] = {}
    for release_id, (event_type, event_name, release_time) in FRED_RELEASES.items():
        payload = fred_get(
            client,
            "release/dates",
            release_id=release_id,
            include_release_dates_with_no_data="true",
            limit=10_000,
            sort_order="asc",
        )
        atomic_text(
            RAW_ROOT / "fred" / f"release-{release_id}.json",
            json.dumps(payload, indent=2) + "\n",
        )
        for item in payload["release_dates"]:
            release_date = date.fromisoformat(item["date"])
            if not START_DATE <= release_date <= END_DATE:
                continue
            local_dt = datetime.combine(release_date, release_time, tzinfo=NY)
            events.append(
                event_row(
                    event_date=release_date,
                    event_ts_utc=local_dt.astimezone(UTC),
                    event_time_et=release_time.isoformat(),
                    event_type=event_type,
                    event_name=event_name,
                    source="FRED release calendar",
                    source_url=(
                        "https://fred.stlouisfed.org/docs/api/fred/release_dates.html"
                    ),
                    time_basis="standard_release_time",
                    details={
                        "release_id": release_id,
                        "release_last_updated": item.get("release_last_updated"),
                    },
                )
            )
        summary[event_type] = sum(e["event_type"] == event_type for e in events)
    frame = pl.DataFrame(events).sort(["event_date", "event_type"])
    atomic_parquet(frame, NORMALIZED_ROOT / "events" / "economic-releases.parquet")
    return events, summary


MONTHS = {name: number for number, name in enumerate(calendar.month_name) if name}
MONTHS.update(
    {name: number for number, name in enumerate(calendar.month_abbr) if name}
)


def parse_meeting_dates(year: int, month_text: str, day_text: str) -> tuple[date, date]:
    months = month_text.split("/")
    start_month = MONTHS[months[0]]
    end_month = MONTHS[months[-1]]
    clean_days = re.sub(r"[^0-9-]", "", day_text)
    parts = clean_days.split("-")
    start_day = int(parts[0])
    end_day = int(parts[-1])
    end_year = year + (1 if end_month < start_month else 0)
    return date(year, start_month, start_day), date(end_year, end_month, end_day)


def fetch_fomc(client: httpx.Client) -> tuple[list[dict], dict]:
    meetings: list[dict] = []
    historical_pattern = re.compile(
        r"^(?P<month>[A-Za-z]+(?:/[A-Za-z]+)?)\s+"
        r"(?P<days>[0-9]+(?:-[0-9]+)?)(?P<flags>.*?)\s+Meeting\s+-\s+(?P<year>[0-9]{4})$"
    )
    for year in range(START_DATE.year, 2021):
        url = f"https://www.federalreserve.gov/monetarypolicy/fomchistorical{year}.htm"
        response = client.get(url)
        response.raise_for_status()
        atomic_bytes(RAW_ROOT / "federal-reserve" / f"fomc-{year}.html", response.content)
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup.find_all(["h4", "h5"]):
            text_value = " ".join(tag.get_text(" ", strip=True).split())
            match = historical_pattern.match(text_value)
            if not match:
                continue
            start_date, end_date = parse_meeting_dates(
                int(match["year"]), match["month"], match["days"]
            )
            flags = match["flags"].lower()
            status = "cancelled" if "cancelled" in flags else "held"
            if "unscheduled" in flags:
                status = "unscheduled"
            meetings.append(
                event_row(
                    event_date=end_date,
                    event_type="fomc",
                    event_name="FOMC meeting decision date",
                    source="Federal Reserve",
                    source_url=url,
                    status=status,
                    details={
                        "meeting_start": start_date.isoformat(),
                        "meeting_end": end_date.isoformat(),
                        "raw_heading": text_value,
                    },
                )
            )

    current_url = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
    response = client.get(current_url)
    response.raise_for_status()
    atomic_bytes(RAW_ROOT / "federal-reserve" / "fomc-current.html", response.content)
    soup = BeautifulSoup(response.text, "html.parser")
    for panel in soup.select("div.panel.panel-default"):
        heading = panel.find("h4")
        if not heading:
            continue
        year_match = re.search(r"([0-9]{4}) FOMC Meetings", heading.get_text(" ", strip=True))
        if not year_match:
            continue
        year = int(year_match.group(1))
        for row in panel.select("div.fomc-meeting"):
            month_node = row.select_one(".fomc-meeting__month")
            date_node = row.select_one(".fomc-meeting__date")
            if not month_node or not date_node:
                continue
            month_text = month_node.get_text(" ", strip=True)
            day_text = date_node.get_text(" ", strip=True)
            start_date, end_date = parse_meeting_dates(year, month_text, day_text)
            if not START_DATE <= end_date <= END_DATE:
                continue
            meetings.append(
                event_row(
                    event_date=end_date,
                    event_type="fomc",
                    event_name="FOMC meeting decision date",
                    source="Federal Reserve",
                    source_url=current_url,
                    status="scheduled_or_held",
                    details={
                        "meeting_start": start_date.isoformat(),
                        "meeting_end": end_date.isoformat(),
                        "raw_month": month_text,
                        "raw_days": day_text,
                    },
                )
            )

    unique = {
        (item["event_date"], item["status"], item["details_json"]): item
        for item in meetings
    }
    meetings = sorted(unique.values(), key=lambda row: row["event_date"])
    atomic_parquet(
        pl.DataFrame(meetings),
        NORMALIZED_ROOT / "events" / "fomc-meetings.parquet",
    )
    return meetings, {
        "rows": len(meetings),
        "start": str(meetings[0]["event_date"]),
        "end": str(meetings[-1]["event_date"]),
    }


def fetch_one_earnings(symbol: str) -> tuple[str, list[dict]]:
    frame = yf.Ticker(symbol).get_earnings_dates(limit=100)
    if frame is None or frame.empty:
        raise RuntimeError("No earnings dates returned")
    events: list[dict] = []
    source_rows: list[dict] = []
    for timestamp, item in frame.iterrows():
        ts = pd.Timestamp(timestamp)
        if ts.tzinfo is None:
            ts = ts.tz_localize("America/New_York")
        ts_utc = ts.tz_convert("UTC").to_pydatetime()
        event_date = ts.tz_convert("America/New_York").date()
        if event_date < START_DATE:
            continue
        estimate = item.get("EPS Estimate")
        reported = item.get("Reported EPS")
        surprise = item.get("Surprise(%)")
        details = {
            "eps_estimate": None if pd.isna(estimate) else float(estimate),
            "reported_eps": None if pd.isna(reported) else float(reported),
            "surprise_pct": None if pd.isna(surprise) else float(surprise),
        }
        source_rows.append(
            {
                "symbol": symbol,
                "earnings_ts_utc": ts_utc,
                "earnings_date_et": event_date,
                **details,
                "source": "Yahoo Finance via yfinance",
            }
        )
        events.append(
            event_row(
                event_date=event_date,
                event_ts_utc=ts_utc,
                event_time_et=ts.tz_convert("America/New_York").strftime("%H:%M:%S"),
                event_type="mega_cap_earnings",
                event_name=f"{symbol} earnings",
                symbol=symbol,
                source="Yahoo Finance via yfinance",
                source_url=f"https://finance.yahoo.com/quote/{symbol}/",
                time_basis="source_timestamp",
                details=details,
            )
        )
    atomic_parquet(
        pl.DataFrame(source_rows).sort("earnings_ts_utc"),
        NORMALIZED_ROOT / "earnings" / f"{symbol}.parquet",
    )
    return symbol, events


def fetch_earnings() -> tuple[list[dict], dict]:
    yf.config.network.retries = 3
    events: list[dict] = []
    errors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(fetch_one_earnings, symbol): symbol for symbol in MEGA_CAP_SYMBOLS}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                _, rows = future.result()
                events.extend(rows)
            except Exception as exc:
                errors[symbol] = f"{type(exc).__name__}: {exc}"
    if events:
        events.sort(key=lambda row: (row["event_date"], row["symbol"] or ""))
        atomic_parquet(
            pl.DataFrame(events),
            NORMALIZED_ROOT / "events" / "mega-cap-earnings.parquet",
        )
    return events, {
        "rows": len(events),
        "symbols_requested": len(MEGA_CAP_SYMBOLS),
        "symbols_completed": len(MEGA_CAP_SYMBOLS) - len(errors),
        "errors": errors,
    }


def third_friday(year: int, month: int) -> date:
    weeks = calendar.monthcalendar(year, month)
    fridays = [week[calendar.FRIDAY] for week in weeks if week[calendar.FRIDAY]]
    return date(year, month, fridays[2])


def build_market_calendar() -> tuple[list[dict], dict]:
    xnys = xcals.get_calendar(
        "XNYS", start=START_DATE.isoformat(), end=END_DATE.isoformat()
    )
    schedule = xnys.schedule.loc[START_DATE.isoformat() : END_DATE.isoformat()]
    sessions = {timestamp.date() for timestamp in schedule.index}

    def previous_session(value: date) -> date:
        cursor = value
        while cursor not in sessions:
            cursor -= timedelta(days=1)
        return cursor

    events: list[dict] = []
    half_days = 0
    for session, row in schedule.iterrows():
        close_utc = pd.Timestamp(row["close"])
        close_et = close_utc.tz_convert("America/New_York")
        if close_et.time() >= time(16):
            continue
        half_days += 1
        events.append(
            event_row(
                event_date=session.date(),
                event_ts_utc=close_utc.to_pydatetime(),
                event_time_et=close_et.strftime("%H:%M:%S"),
                event_type="us_equity_half_day",
                event_name="US equity early close",
                source="exchange_calendars XNYS",
                source_url="https://pypi.org/project/exchange-calendars/",
                time_basis="calendar_close",
            )
        )

    opex_count = 0
    roll_count = 0
    for year in range(START_DATE.year, END_DATE.year + 1):
        for month in range(1, 13):
            nominal_expiry = third_friday(year, month)
            if not START_DATE <= nominal_expiry <= END_DATE:
                continue
            expiry_session = previous_session(nominal_expiry)
            quarterly = month in (3, 6, 9, 12)
            opex_count += 1
            events.append(
                event_row(
                    event_date=expiry_session,
                    event_type="quarterly_opex" if quarterly else "monthly_opex",
                    event_name="US monthly option expiration",
                    source="standard US option expiration convention + XNYS calendar",
                    source_url="https://www.cboe.com/tradable_products/",
                    details={
                        "nominal_third_friday": nominal_expiry.isoformat(),
                        "holiday_adjusted": expiry_session != nominal_expiry,
                    },
                )
            )
            if quarterly:
                roll_date = nominal_expiry - timedelta(days=4)
                roll_count += 1
                events.append(
                    event_row(
                        event_date=roll_date,
                        event_type="cme_equity_index_roll",
                        event_name="CME equity-index customary roll date",
                        source="CME Group",
                        source_url="https://www.cmegroup.com/trading/equity-index/rolldates.html",
                        details={
                            "nominal_expiration": nominal_expiry.isoformat(),
                            "expiration_session": expiry_session.isoformat(),
                            "roots": ["NQ", "ES", "YM", "RTY"],
                        },
                    )
                )

    events.sort(key=lambda row: (row["event_date"], row["event_type"]))
    atomic_parquet(
        pl.DataFrame(events),
        NORMALIZED_ROOT / "events" / "market-calendar.parquet",
    )
    return events, {
        "half_days": half_days,
        "option_expirations": opex_count,
        "cme_roll_dates": roll_count,
        "start": START_DATE.isoformat(),
        "end": END_DATE.isoformat(),
    }


def main() -> int:
    load_dotenv(ROOT / ".env")
    if not os.getenv("FRED_API_KEY"):
        raise SystemExit(f"Missing FRED_API_KEY in {ROOT / '.env'}")
    for directory in (RAW_ROOT, NORMALIZED_ROOT, MANIFEST_ROOT):
        directory.mkdir(parents=True, exist_ok=True)

    headers = {"User-Agent": "Mozilla/5.0 market-research-data-pull"}
    timeout = httpx.Timeout(60, connect=15)
    transport = httpx.HTTPTransport(retries=4)
    generated_at = datetime.now(tz=UTC)
    with httpx.Client(
        headers=headers,
        timeout=timeout,
        transport=transport,
        follow_redirects=True,
    ) as client:
        _, fred_summary = fetch_fred_volatility(client)
        vvix_summary = fetch_vvix(client)
        economic_events, release_summary = fetch_fred_release_calendars(client)
        fomc_events, fomc_summary = fetch_fomc(client)

    earnings_events, earnings_summary = fetch_earnings()
    market_events, market_summary = build_market_calendar()
    all_events = economic_events + fomc_events + earnings_events + market_events
    all_events.sort(
        key=lambda row: (
            row["event_date"],
            row["event_type"],
            row["symbol"] or "",
        )
    )
    atomic_parquet(
        pl.DataFrame(all_events),
        NORMALIZED_ROOT / "events" / "combined-event-calendar.parquet",
    )

    manifest = {
        "status": "complete" if not earnings_summary["errors"] else "complete_with_warnings",
        "generated_at": generated_at.isoformat(),
        "volatility": {"fred": fred_summary, "vvix": vvix_summary},
        "events": {
            "economic_releases": release_summary,
            "fomc": fomc_summary,
            "earnings": earnings_summary,
            "market_calendar": market_summary,
            "combined_rows": len(all_events),
        },
        "sources": {
            "fred": "https://api.stlouisfed.org/fred/",
            "cboe_vvix": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VVIX_History.csv",
            "federal_reserve": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            "earnings": "Yahoo Finance via yfinance",
            "market_sessions": "exchange_calendars XNYS",
            "cme_roll_rule": "Monday before the third Friday",
        },
    }
    atomic_text(
        MANIFEST_ROOT / "external-context.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    print(json.dumps(manifest, sort_keys=True), flush=True)
    return 0 if manifest["status"] == "complete" else 1


if __name__ == "__main__":
    raise SystemExit(main())
