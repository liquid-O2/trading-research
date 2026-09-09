#!/usr/bin/env python3
"""Download the small market dependencies required by the options datasets.

The downloader keeps source responses and writes normalized, zstd-compressed
Parquet atomically. It does not aggregate or consolidate the source records.
"""

from __future__ import annotations

import argparse
import io
import json
import os
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import httpx
import pandas as pd
import polars as pl
import yfinance as yf
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "data" / "market-dependencies"
RAW_ROOT = OUTPUT_ROOT / "raw"
NORMALIZED_ROOT = OUTPUT_ROOT / "normalized"
MANIFEST_ROOT = ROOT / "manifests"
START_DATE = date(2010, 1, 1)
VX_START_DATE = date(2020, 1, 1)

FRED_SERIES = {
    "DFF": ("effective_federal_funds", 1),
    "SOFR": ("secured_overnight_financing_rate", 1),
    "DGS1MO": ("treasury_constant_maturity_1m", 30),
    "DTB3": ("treasury_bill_secondary_market_3m", 91),
    "DGS3MO": ("treasury_constant_maturity_3m", 91),
    "DGS6MO": ("treasury_constant_maturity_6m", 182),
    "DGS1": ("treasury_constant_maturity_1y", 365),
}

CASH_SYMBOLS = {
    "QQQ": "QQQ",
    "SPY": "SPY",
    "NDX": "^NDX",
    "SPX": "^GSPC",
}

ETF_SYMBOLS = ("QQQ", "SPY")
CBOE_VX_LIST_URL = (
    "https://www-api.cboe.com/us/futures/market_statistics/"
    "historical_data/product/list/VX/"
)
CBOE_CDN = "https://cdn.cboe.com/"
CBOE_VOLUME_OI_URL = (
    "https://cdn.cboe.com/data/us/futures/market_statistics/"
    "historical_data/cfevoloi.csv"
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
    response = client.get(
        f"https://api.stlouisfed.org/fred/{endpoint}",
        params={
            "api_key": os.environ["FRED_API_KEY"],
            "file_type": "json",
            **params,
        },
    )
    response.raise_for_status()
    return response.json()


def fetch_rates(client: httpx.Client) -> dict:
    rows: list[dict] = []
    series_summary: dict[str, dict] = {}
    today = date.today().isoformat()
    for series_id, (name, tenor_days) in FRED_SERIES.items():
        info = fred_get(client, "series", series_id=series_id)
        observations = fred_get(
            client,
            "series/observations",
            series_id=series_id,
            observation_start=START_DATE.isoformat(),
            observation_end=today,
        )
        atomic_text(
            RAW_ROOT / "fred" / f"{series_id}.json",
            json.dumps(
                {"series": info, "observations": observations},
                indent=2,
                sort_keys=True,
            )
            + "\n",
        )
        valid = 0
        for item in observations["observations"]:
            value = None if item["value"] == "." else float(item["value"])
            valid += value is not None
            rows.append(
                {
                    "date": date.fromisoformat(item["date"]),
                    "series_id": series_id,
                    "name": name,
                    "tenor_days": tenor_days,
                    "rate_pct": value,
                    "realtime_start": date.fromisoformat(item["realtime_start"]),
                    "realtime_end": date.fromisoformat(item["realtime_end"]),
                    "source": "FRED",
                }
            )
        series_summary[series_id] = {
            "rows": len(observations["observations"]),
            "valid_rows": valid,
        }
    frame = pl.DataFrame(rows).sort(["date", "tenor_days", "series_id"])
    atomic_parquet(frame, NORMALIZED_ROOT / "rates" / "usd-rates.parquet")
    return {"rows": frame.height, "series": series_summary}


def flatten_yahoo_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    if isinstance(frame.columns, pd.MultiIndex):
        frame.columns = [str(column[0]) for column in frame.columns]
    else:
        frame.columns = [str(column) for column in frame.columns]
    return frame


def fetch_cash_daily() -> dict:
    summaries: dict[str, dict] = {}
    end = date.today() + timedelta(days=1)
    for symbol, yahoo_symbol in CASH_SYMBOLS.items():
        frame = yf.download(
            yahoo_symbol,
            start=START_DATE.isoformat(),
            end=end.isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=False,
            progress=False,
            threads=False,
        )
        if frame.empty:
            raise RuntimeError(f"Yahoo returned no daily data for {yahoo_symbol}")
        frame = flatten_yahoo_columns(frame)
        frame.index.name = "date"
        frame = frame.reset_index()
        raw_path = RAW_ROOT / "yahoo" / "daily" / f"{symbol}.csv"
        atomic_text(raw_path, frame.to_csv(index=False))
        rename_candidates = {
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adjusted_close",
            "Volume": "volume",
        }
        normalized = pl.from_pandas(frame).rename(
            {
                source: target
                for source, target in rename_candidates.items()
                if source in frame.columns
            }
        )
        normalized = normalized.with_columns(
            pl.col("date").cast(pl.Date),
            pl.lit(symbol).alias("symbol"),
            pl.lit(yahoo_symbol).alias("source_symbol"),
            pl.lit("Yahoo Finance").alias("source"),
        ).select(
            "date",
            "symbol",
            "source_symbol",
            "open",
            "high",
            "low",
            "close",
            "adjusted_close",
            "volume",
            "source",
        ).sort("date")
        output = NORMALIZED_ROOT / "cash-daily" / f"{symbol}.parquet"
        atomic_parquet(normalized, output)
        summaries[symbol] = {
            "rows": normalized.height,
            "start": str(normalized["date"].min()),
            "end": str(normalized["date"].max()),
        }
    return summaries


def fetch_corporate_actions() -> dict:
    summaries: dict[str, dict] = {}
    for symbol in ETF_SYMBOLS:
        history = yf.Ticker(symbol).history(
            start=START_DATE.isoformat(),
            end=(date.today() + timedelta(days=1)).isoformat(),
            interval="1d",
            auto_adjust=False,
            actions=True,
        )
        if history.empty:
            raise RuntimeError(f"Yahoo returned no corporate-action history for {symbol}")
        action_rows: list[dict] = []
        for timestamp, row in history.iterrows():
            dividend = float(row.get("Dividends", 0.0) or 0.0)
            split_ratio = float(row.get("Stock Splits", 0.0) or 0.0)
            if dividend == 0.0 and split_ratio == 0.0:
                continue
            action_rows.append(
                {
                    "ex_date": pd.Timestamp(timestamp).date(),
                    "symbol": symbol,
                    "dividend": dividend,
                    "split_ratio": split_ratio,
                    "source": "Yahoo Finance",
                }
            )
        frame = pl.DataFrame(
            action_rows,
            schema={
                "ex_date": pl.Date,
                "symbol": pl.String,
                "dividend": pl.Float64,
                "split_ratio": pl.Float64,
                "source": pl.String,
            },
        ).sort("ex_date")
        atomic_parquet(
            frame,
            NORMALIZED_ROOT / "corporate-actions" / f"{symbol}.parquet",
        )
        summaries[symbol] = {
            "rows": frame.height,
            "dividends": frame.filter(pl.col("dividend") != 0).height,
            "splits": frame.filter(pl.col("split_ratio") != 0).height,
        }
    return summaries


def numeric_series(frame: pd.DataFrame, source: str) -> pd.Series:
    if source not in frame.columns:
        return pd.Series([None] * len(frame), index=frame.index, dtype="float64")
    cleaned = frame[source].astype(str).str.replace(",", "", regex=False)
    return pd.to_numeric(cleaned, errors="coerce")


def fetch_vx_curve(client: httpx.Client) -> dict:
    listing_response = client.get(CBOE_VX_LIST_URL)
    listing_response.raise_for_status()
    listing = listing_response.json()
    atomic_text(
        RAW_ROOT / "cboe" / "vx-futures" / "contract-list.json",
        json.dumps(listing, indent=2, sort_keys=True) + "\n",
    )

    contracts: list[dict] = []
    seen_paths: set[str] = set()
    for entries in listing.values():
        for entry in entries:
            expiry = date.fromisoformat(entry["expire_date"])
            if expiry < VX_START_DATE or entry["path"] in seen_paths:
                continue
            seen_paths.add(entry["path"])
            contracts.append(entry)
    contracts.sort(key=lambda item: (item["expire_date"], item["path"]))

    rows: list[pd.DataFrame] = []
    failures: list[dict] = []
    for index, contract in enumerate(contracts, start=1):
        expiry = date.fromisoformat(contract["expire_date"])
        raw_path = RAW_ROOT / "cboe" / "vx-futures" / f"{expiry.isoformat()}.csv"
        try:
            if raw_path.exists() and raw_path.stat().st_size:
                payload = raw_path.read_bytes()
            else:
                response = client.get(CBOE_CDN + contract["path"])
                response.raise_for_status()
                payload = response.content
                atomic_bytes(raw_path, payload)
            source = pd.read_csv(io.BytesIO(payload))
            if source.empty:
                continue
            normalized = pd.DataFrame(
                {
                    "trade_date": pd.to_datetime(
                        source["Trade Date"], errors="coerce"
                    ).dt.date,
                    "root": "VX",
                    "contract_expiration": expiry,
                    "duration_type": contract.get("duration_type"),
                    "product_display": contract.get("product_display"),
                    "contract_label": source.get("Futures"),
                    "open": numeric_series(source, "Open"),
                    "high": numeric_series(source, "High"),
                    "low": numeric_series(source, "Low"),
                    "close": numeric_series(source, "Close"),
                    "settlement": numeric_series(source, "Settle"),
                    "change": numeric_series(source, "Change"),
                    "total_volume": numeric_series(source, "Total Volume"),
                    "efp": numeric_series(source, "EFP"),
                    "open_interest": numeric_series(source, "Open Interest"),
                    "source": "Cboe",
                }
            )
            normalized = normalized[
                normalized["trade_date"].notna()
                & (normalized["trade_date"] >= VX_START_DATE)
                & (normalized["trade_date"] <= date.today())
            ]
            if not normalized.empty:
                rows.append(normalized)
        except Exception as exc:
            failures.append(
                {
                    "path": contract["path"],
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
        if index % 50 == 0:
            print(f"VX contracts processed: {index}/{len(contracts)}", flush=True)

    if failures:
        raise RuntimeError(f"VX contract failures: {json.dumps(failures[:10])}")
    if not rows:
        raise RuntimeError("Cboe returned no VX curve rows")
    combined = pd.concat(rows, ignore_index=True)
    frame = pl.from_pandas(combined).with_columns(
        pl.col("trade_date").cast(pl.Date),
        pl.col("contract_expiration").cast(pl.Date),
        pl.col("total_volume").cast(pl.Int64, strict=False),
        pl.col("efp").cast(pl.Int64, strict=False),
        pl.col("open_interest").cast(pl.Int64, strict=False),
    ).sort(["trade_date", "contract_expiration", "duration_type"])
    atomic_parquet(frame, NORMALIZED_ROOT / "vx-futures" / "all-contracts.parquet")

    product_response = client.get(CBOE_VOLUME_OI_URL)
    product_response.raise_for_status()
    atomic_bytes(
        RAW_ROOT / "cboe" / "cfevoloi.csv",
        product_response.content,
    )
    return {
        "contracts": len(contracts),
        "rows": frame.height,
        "start": str(frame["trade_date"].min()),
        "end": str(frame["trade_date"].max()),
        "monthly_contract_rows": frame.filter(pl.col("duration_type") == "M").height,
        "weekly_contract_rows": frame.filter(pl.col("duration_type") == "W").height,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--component",
        action="append",
        choices=("rates", "cash", "vx"),
        help="Run only selected components; may be repeated.",
    )
    args = parser.parse_args()
    selected = set(args.component or ("rates", "cash", "vx"))

    load_dotenv(ROOT / ".env")
    if "rates" in selected and not os.getenv("FRED_API_KEY"):
        raise SystemExit(f"Missing FRED_API_KEY in {ROOT / '.env'}")
    for directory in (RAW_ROOT, NORMALIZED_ROOT, MANIFEST_ROOT):
        directory.mkdir(parents=True, exist_ok=True)

    result: dict[str, object] = {
        "status": "complete",
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "components": {},
    }
    timeout = httpx.Timeout(90, connect=20)
    transport = httpx.HTTPTransport(retries=5)
    headers = {"User-Agent": "Mozilla/5.0 market-research-data-pull"}
    with httpx.Client(
        timeout=timeout,
        transport=transport,
        headers=headers,
        follow_redirects=True,
    ) as client:
        if "rates" in selected:
            result["components"]["rates"] = fetch_rates(client)
        if "cash" in selected:
            result["components"]["cash_daily"] = fetch_cash_daily()
            result["components"]["corporate_actions"] = fetch_corporate_actions()
        if "vx" in selected:
            result["components"]["vx_curve"] = fetch_vx_curve(client)

    manifest_path = MANIFEST_ROOT / "market-dependencies.json"
    previous: dict = {}
    if manifest_path.exists():
        try:
            previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous = {}
    merged_components = {
        **previous.get("components", {}),
        **result["components"],
    }
    result["components"] = merged_components
    atomic_text(manifest_path, json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
