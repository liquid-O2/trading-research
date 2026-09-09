#!/usr/bin/env python3
"""Build a shallow, model-readable archive and optionally upload it to R2.

The archive is a hard-linked view of completed source files.  It does not
rewrite, combine, resample, or duplicate the market data on the RunPod volume.
Incomplete ``*.part`` files and explicitly excluded superseded samples are
recorded in the manifests but never staged.
"""

from __future__ import annotations

import argparse
import csv
import errno
import fnmatch
import json
import os
import re
import subprocess
import time
from dataclasses import asdict, dataclass, field
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any, Iterable

import pyarrow as pa
import pyarrow.parquet as pq


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_STAGE_ROOT = Path("/workspace/r2-upload/data")
DEFAULT_LEGACY_ROOT = Path("/workspace/data")
DEFAULT_RCLONE_CONFIG = Path("/workspace/.config/rclone/rclone.conf")
DEFAULT_REMOTE = "r2:data"
ROLL_MAP_ROOTS = ("NQ", "ES", "YM")


TIMESTAMP_PROFILES: dict[str, dict[str, Any]] = {
    "quantpad-tick-ns-utc": {
        "source_timezone": "UTC",
        "stored_timezone": "UTC (integer epoch fields are timezone-naive by type)",
        "stored_type": "int64 Unix epoch",
        "stored_unit": "nanoseconds",
        "effective_precision": "nanoseconds",
        "dst_handling": "not applicable after UTC normalization",
        "fields": {
            "t": "event timestamp",
            "ts_recv": "receive timestamp when present",
            "ts_ref": "reference timestamp when present",
            "expiration": "contract expiration when present",
            "activation": "contract activation when present",
        },
        "conversion": "QuantPad Arrow output retained without timestamp rewriting.",
    },
    "quantpad-bar-ms-utc": {
        "source_timezone": "UTC",
        "stored_timezone": "UTC (integer epoch field is timezone-naive by type)",
        "stored_type": "int64 Unix epoch",
        "stored_unit": "milliseconds",
        "effective_precision": "milliseconds",
        "dst_handling": "not applicable after UTC normalization",
        "fields": {"t": "bar interval start timestamp"},
        "conversion": "QuantPad Arrow output retained without timestamp rewriting.",
    },
    "continuous-roll-map-mixed-utc": {
        "source_timezone": "UTC",
        "stored_timezone": "UTC in explicit Arrow timestamp companion fields",
        "stored_type": "mixed int64 Unix epochs plus Arrow timestamps",
        "stored_unit": "milliseconds for bar/segment epoch fields; nanoseconds for definition epoch fields",
        "effective_precision": "milliseconds for bar-derived fields; nanoseconds for definition-derived fields",
        "dst_handling": "not applicable after UTC normalization",
        "fields": {
            "first_bar_ms": "first observed continuous-contract bar timestamp in Unix epoch milliseconds",
            "last_bar_ms": "last observed continuous-contract bar timestamp in Unix epoch milliseconds",
            "segment_start_ms": "roll-segment start in Unix epoch milliseconds",
            "segment_end_exclusive_ms": "next roll-segment start in Unix epoch milliseconds",
            "expiration": "contract expiration in Unix epoch nanoseconds",
            "activation": "contract activation in Unix epoch nanoseconds",
            "first_definition_ns": "first definition event in Unix epoch nanoseconds",
            "last_definition_ns": "last definition event in Unix epoch nanoseconds",
        },
        "conversion": "Epoch values are retained and paired with explicit Arrow timestamp columns normalized to UTC.",
    },
    "databento-dbn-ns-utc": {
        "source_timezone": "UTC",
        "stored_timezone": "UTC in native DBN records",
        "stored_type": "Databento Binary Encoding (DBN), Zstandard compressed",
        "stored_unit": "nanoseconds for DBN timestamp fields",
        "effective_precision": "nanoseconds",
        "dst_handling": "not applicable after UTC normalization",
        "fields": {
            "ts_event": "exchange event timestamp",
            "ts_recv": "Databento receive timestamp where supplied by the schema",
        },
        "conversion": "Original Databento .dbn.zst files are byte-identical and unconverted.",
    },
    "thetadata-ms-et-to-ns-utc": {
        "source_timezone": "America/New_York",
        "stored_timezone": "UTC",
        "stored_type": "Arrow timestamp[ns, tz=UTC]",
        "stored_unit": "nanoseconds",
        "effective_precision": "milliseconds (the source terminal supplies milliseconds)",
        "dst_handling": (
            "Source wall times were localized with the IANA America/New_York zone, "
            "ambiguous fall-back times choose the earliest occurrence, nonexistent "
            "spring-forward times become null, then values were converted to UTC."
        ),
        "fields": {
            "ts_event": "option quote/trade/open-interest event time when present",
            "ts_quote": "NBBO timestamp paired with a trade when present",
            "ts_created": "ThetaData record creation timestamp when present",
            "ts_last_trade": "last-trade timestamp when present",
            "request_date": "exchange-session date used for the request",
        },
        "conversion": (
            "ThetaData terminal strings with millisecond precision were converted during "
            "ingestion; no additional conversion is performed by this archive builder."
        ),
    },
    "date-only": {
        "source_timezone": "calendar date",
        "stored_timezone": None,
        "stored_type": "Arrow date32 or source text date",
        "stored_unit": "days",
        "effective_precision": "one day",
        "dst_handling": "not applicable",
        "fields": {"date": "observation or session date"},
        "conversion": "No intraday timestamp is implied by a date-only field.",
    },
    "mixed-free-source": {
        "source_timezone": "source-specific; see schema and dataset notes",
        "stored_timezone": "UTC for explicit normalized timestamps; otherwise date-only",
        "stored_type": "mixed Parquet, CSV, JSON, and HTML",
        "stored_unit": "source-specific",
        "effective_precision": "source-specific",
        "dst_handling": "source-specific",
        "fields": {},
        "conversion": "Raw source responses and normalized companions are separated by dataset.",
    },
}


@dataclass(frozen=True)
class DatasetSpec:
    provider: str
    archive_name: str
    source: Path
    venue_dataset: str
    symbol: str
    asset_class: str
    schema: str
    granularity: str
    partitioning: str
    timestamp_profile: str
    scope: str
    description: str
    status: str = "complete"
    adjustment: str = "none; values are retained as acquired"
    expected_start: str | None = None
    expected_end: str | None = None
    known_gaps: tuple[str, ...] = ()
    flatten: bool = True
    tags: tuple[str, ...] = ()
    include_patterns: tuple[str, ...] = ("*",)

    @property
    def dataset_id(self) -> str:
        return f"{self.provider}/{self.archive_name}"


def quantpad_specs(source_root: Path) -> list[DatasetSpec]:
    data = source_root / "data"
    specs: list[DatasetSpec] = []
    roots = {
        "nq-c-0": ("NQ.c.0", "NQ futures", "nq-continuous-futures"),
        "es-c-0": ("ES.c.0", "ES futures", "es-continuous-futures"),
        "ym-c-0": ("YM.c.0", "YM futures", "ym-continuous-futures"),
        "rty-c-0": ("RTY.c.0", "RTY futures", "rty-continuous-futures"),
    }
    bar_granularity = {
        "ohlcv-1m": "one-minute OHLCV bars",
        "ohlcv-1s": "one-second OHLCV bars",
    }
    for slug, (symbol, label, asset_slug) in roots.items():
        base = data / "phase-1" / "glbx-mdp3" / slug
        for schema in ("ohlcv-1m", "statistics", "definition"):
            if schema.startswith("ohlcv"):
                granularity = bar_granularity[schema]
                timestamp_profile = "quantpad-bar-ms-utc"
            elif schema == "statistics":
                granularity = "exchange statistics events, including settlement/open interest updates"
                timestamp_profile = "quantpad-tick-ns-utc"
            else:
                granularity = "instrument-definition events"
                timestamp_profile = "quantpad-tick-ns-utc"
            rty_definition_skipped = slug == "rty-c-0" and schema == "definition"
            specs.append(
                DatasetSpec(
                    provider="quantpad",
                    archive_name=f"cme__{asset_slug}__{schema}",
                    source=base / schema,
                    venue_dataset="GLBX.MDP3",
                    symbol=symbol,
                    asset_class="continuous futures",
                    schema=schema,
                    granularity=granularity,
                    partitioning="calendar year",
                    timestamp_profile=timestamp_profile,
                    scope="full available continuous-contract history",
                    description=f"QuantPad-routed Databento CME {label} {schema} data.",
                    status="partial-skipped" if rty_definition_skipped else "complete",
                    expected_start="2010-09",
                    known_gaps=(
                        "RTY definition years 2010-2018 were intentionally skipped after repeated vendor read timeouts; 2019-2026 are retained.",
                    ) if rty_definition_skipped else (),
                    tags=("CME", "continuous", "raw", "unadjusted"),
                )
            )
    specs.append(
        DatasetSpec(
            provider="quantpad",
            archive_name="cme__nq-continuous-futures__ohlcv-1s",
            source=data / "phase-1/glbx-mdp3/nq-c-0/ohlcv-1s",
            venue_dataset="GLBX.MDP3",
            symbol="NQ.c.0",
            asset_class="continuous futures",
            schema="ohlcv-1s",
            granularity="one-second OHLCV bars",
            partitioning="calendar year/month as acquired",
            timestamp_profile="quantpad-bar-ms-utc",
            scope="full available continuous-contract history",
            description="QuantPad-routed Databento CME NQ continuous one-second bars.",
            expected_start="2010-09",
            tags=("CME", "continuous", "raw", "unadjusted"),
        )
    )
    for slug, (symbol, label, asset_slug) in roots.items():
        trade_dir = data / "phase-4" / "glbx-mdp3" / slug / "trades"
        specs.append(
            DatasetSpec(
                provider="quantpad",
                archive_name=f"cme__{asset_slug}__trades",
                source=trade_dir,
                venue_dataset="GLBX.MDP3",
                symbol=symbol,
                asset_class="continuous futures",
                schema="trades",
                granularity="individual trade events",
                partitioning="calendar month",
                timestamp_profile="quantpad-tick-ns-utc",
                scope="2020 onward, continuous front contract",
                description=f"QuantPad-routed Databento CME {label} trade tape.",
                expected_start="2020-01",
                tags=("CME", "continuous", "raw", "unadjusted"),
            )
        )
    for slug, asset_slug, symbol, status, gaps in (
        ("nq-c-0", "nq-continuous-futures", "NQ.c.0", "complete", ()),
        (
            "es-c-0",
            "es-continuous-futures",
            "ES.c.0",
            "partial-paused",
            ("The six-year ES MBP-1 pull was intentionally paused; see computed missing_months.",),
        ),
    ):
        specs.append(
            DatasetSpec(
                provider="quantpad",
                archive_name=f"cme__{asset_slug}__mbp-1",
                source=data / "phase-4" / "glbx-mdp3" / slug / "mbp-1",
                venue_dataset="GLBX.MDP3",
                symbol=symbol,
                asset_class="continuous futures",
                schema="mbp-1",
                granularity="every top-of-book market-by-price update",
                partitioning="calendar month",
                timestamp_profile="quantpad-tick-ns-utc",
                scope="2020 onward, continuous front contract",
                description=f"QuantPad-routed Databento CME {symbol} level-1 order-book updates.",
                status=status,
                expected_start="2020-01",
                known_gaps=gaps,
                tags=("CME", "continuous", "raw", "unadjusted", "tick"),
            )
        )
    for archive_name, source, dataset, symbol in (
        (
            "nasdaq__qqq-etf__ohlcv-1m",
            data / "phase-2/xnas-itch/qqq/ohlcv-1m",
            "XNAS.ITCH",
            "QQQ",
        ),
        (
            "nyse-arca__spy-etf__ohlcv-1m",
            data / "phase-2/arcx-pillar/spy/ohlcv-1m",
            "ARCX.PILLAR",
            "SPY",
        ),
    ):
        specs.append(
            DatasetSpec(
                provider="quantpad",
                archive_name=archive_name,
                source=source,
                venue_dataset=dataset,
                symbol=symbol,
                asset_class="equity/ETF",
                schema="ohlcv-1m",
                granularity="one-minute OHLCV bars",
                partitioning="calendar year",
                timestamp_profile="quantpad-bar-ms-utc",
                scope="full available history from September 2018 onward",
                description=f"QuantPad underlying spot proxy bars for {symbol}.",
                expected_start="2018-09",
                tags=("underlying", "raw"),
            )
        )
    for root_slug, symbol in (
        ("qqq-opt", "QQQ.OPT"),
        ("ndxp-opt", "NDXP.OPT"),
        ("ndx-opt", "NDX.OPT"),
    ):
        for schema in ("ohlcv-1d", "statistics"):
            specs.append(
                DatasetSpec(
                    provider="quantpad",
                    archive_name=f"opra__{root_slug.removesuffix('-opt')}-options__{schema}__reference",
                    source=data / "phase-2/opra-pillar" / root_slug / schema,
                    venue_dataset="OPRA.PILLAR",
                    symbol=symbol,
                    asset_class="US listed options",
                    schema=schema,
                    granularity=(
                        "one-day OHLCV per contract"
                        if schema == "ohlcv-1d"
                        else "OPRA statistics events"
                    ),
                    partitioning="calendar month",
                    timestamp_profile=(
                        "quantpad-bar-ms-utc"
                        if schema == "ohlcv-1d"
                        else "quantpad-tick-ns-utc"
                    ),
                    scope="partial reference pull; superseded by the ThetaData OPRA archive",
                    description=(
                        "Partial QuantPad OPRA reference retained for cross-provider validation, "
                        "not the primary options archive."
                    ),
                    status="reference-partial-superseded",
                    tags=("OPRA", "reference", "raw"),
                )
            )
    return specs


def databento_specs(source_root: Path) -> list[DatasetSpec]:
    data = source_root / "data/databento/glbx-mdp3"
    specs: list[DatasetSpec] = []
    for slug, symbol in (("nq-opt", "NQ.OPT"), ("es-opt", "ES.OPT")):
        for schema, granularity in (
            ("definition", "instrument-definition events"),
            ("statistics", "exchange statistics events"),
            ("trades", "individual trade events"),
            ("ohlcv-1m", "one-minute OHLCV bars per option contract"),
        ):
            specs.append(
                DatasetSpec(
                    provider="databento",
                    archive_name=f"cme__{slug.removesuffix('-opt')}-options-on-futures__{schema}",
                    source=data / slug / schema,
                    venue_dataset="GLBX.MDP3",
                    symbol=symbol,
                    asset_class="CME options on futures",
                    schema=schema,
                    granularity=granularity,
                    partitioning="vendor batch files, generally calendar month",
                    timestamp_profile="databento-dbn-ns-utc",
                    scope="2020 onward, full parent option chain",
                    description=(
                        f"Direct Databento CME {symbol} {schema} archive. Files remain in native "
                        "compressed DBN rather than Parquet."
                    ),
                    expected_start="2020-01",
                    tags=("CME", "options-on-futures", "raw", "native-dbn"),
                )
            )
    return specs


def legacy_databento_specs(legacy_root: Path) -> list[DatasetSpec]:
    """Catalog the pre-existing direct Databento HG/SI/NKD archive."""
    specs: list[DatasetSpec] = []
    for symbol in ("HG", "SI", "NKD"):
        source = legacy_root / "mbp1" / symbol
        label = symbol.lower()
        specs.extend(
            [
                DatasetSpec(
                    provider="databento",
                    archive_name=f"cme__{label}-futures__mbp-1",
                    source=source,
                    venue_dataset="GLBX.MDP3",
                    symbol=symbol,
                    asset_class="futures",
                    schema="mbp-1",
                    granularity="every top-of-book market-by-price update",
                    partitioning=("daily source files" if symbol == "SI" else "calendar-year source files"),
                    timestamp_profile="databento-dbn-ns-utc",
                    scope="2021 through the available 2026 endpoint",
                    description=f"Pre-existing direct Databento {symbol} MBP-1 archive in native compressed DBN.",
                    tags=("CME", "futures", "raw", "native-dbn", "legacy-source-tree"),
                    include_patterns=("*.mbp-1.dbn.zst",),
                ),
                DatasetSpec(
                    provider="databento",
                    archive_name=f"cme__{label}-futures__trades",
                    source=source,
                    venue_dataset="GLBX.MDP3",
                    symbol=symbol,
                    asset_class="futures",
                    schema="trades",
                    granularity="individual trade events",
                    partitioning="as acquired",
                    timestamp_profile="databento-dbn-ns-utc",
                    scope="available companion trade tape",
                    description=f"Pre-existing direct Databento {symbol} trade archive in native compressed DBN.",
                    tags=("CME", "futures", "raw", "native-dbn", "legacy-source-tree"),
                    include_patterns=("*.trades.dbn.zst",),
                ),
                DatasetSpec(
                    provider="databento",
                    archive_name=f"cme__{label}-futures__source-metadata",
                    source=source,
                    venue_dataset="GLBX.MDP3",
                    symbol=symbol,
                    asset_class="futures acquisition metadata",
                    schema="manifest/metadata/conditions",
                    granularity="one acquisition record per source artifact",
                    partitioning="small JSON companions",
                    timestamp_profile="databento-dbn-ns-utc",
                    scope="provenance for the matching MBP-1/trades archive",
                    description=f"Databento job manifest, metadata, and condition files for {symbol}.",
                    tags=("metadata", "provenance", "legacy-source-tree"),
                    include_patterns=("*.json", "*.sha256"),
                ),
            ]
        )
    return specs


def theta_specs(source_root: Path) -> list[DatasetSpec]:
    data = source_root / "data/thetadata"
    roots = ("QQQ", "NDXP", "NDX", "SPXW", "SPX", "SPY")
    strike_ranges = {"QQQ": 42, "NDXP": 70, "NDX": 70, "SPXW": 90, "SPX": 90, "SPY": 45}
    specs: list[DatasetSpec] = []
    for symbol in roots:
        for kind, schema, granularity, scope in (
            (
                "contracts",
                "contracts",
                "one contract-list snapshot per exchange date",
                "full option chain: all listed expiries and strikes",
            ),
            (
                "open-interest",
                "open_interest",
                "one open-interest observation per contract per exchange date",
                "full option chain: all listed expiries and strikes",
            ),
            (
                "eod",
                "eod",
                "daily OHLC, volume, and closing NBBO per contract",
                "full option chain: all listed expiries and strikes",
            ),
        ):
            specs.append(
                DatasetSpec(
                    provider="thetadata-opra",
                    archive_name=f"opra__{symbol.lower()}-options__{kind}",
                    source=data / "pull-1" / kind / symbol,
                    venue_dataset="ThetaData Options / OPRA",
                    symbol=symbol,
                    asset_class="US listed options",
                    schema=schema,
                    granularity=granularity,
                    partitioning="one file or explicit empty marker per exchange date",
                    timestamp_profile="thetadata-ms-et-to-ns-utc",
                    scope=scope,
                    description=f"ThetaData daily-board {kind} archive for {symbol} options.",
                    expected_start="2018-01-01" if symbol == "NDXP" else "2016-01-01",
                    tags=("OPRA", "options", "daily-board", "raw-normalized-parquet"),
                )
            )
        for kind, archive_scope, granularity, scope, status in (
            (
                "quote-dte14",
                f"quote-1m__dte14__strike-range{strike_ranges[symbol]}",
                "one-minute NBBO snapshots per selected contract",
                f"DTE <= 14; strike_range={strike_ranges[symbol]} around spot",
                "complete",
            ),
            (
                "quote-dte60-atm10",
                "quote-1m__dte60__atm10",
                "one-minute NBBO snapshots per selected contract",
                "ATM +/- 10 listed strikes for every expiry with DTE <= 60",
                "complete",
            ),
            (
                "quote-dte60-atm3",
                "quote-1m__dte60__atm3-legacy",
                "one-minute NBBO snapshots per selected contract",
                "legacy first pass: ATM +/- 3 listed strikes for DTE <= 60",
                "superseded-subset",
            ),
        ):
            specs.append(
                DatasetSpec(
                    provider="thetadata-opra",
                    archive_name=f"opra__{symbol.lower()}-options__{archive_scope}",
                    source=data / "pull-2" / kind / symbol,
                    venue_dataset="ThetaData Options / OPRA",
                    symbol=symbol,
                    asset_class="US listed options",
                    schema="quote",
                    granularity=granularity,
                    partitioning="one file or explicit empty marker per exchange date",
                    timestamp_profile="thetadata-ms-et-to-ns-utc",
                    scope=scope,
                    description=f"ThetaData intraday quote surface for {symbol} options.",
                    status=status,
                    expected_start="2020-01-01",
                    tags=("OPRA", "options", "intraday", "NBBO", "raw-normalized-parquet"),
                )
            )
        specs.append(
            DatasetSpec(
                provider="thetadata-opra",
                archive_name=(
                    f"opra__{symbol.lower()}-options__trade-quote__dte7__"
                    f"strike-range{strike_ranges[symbol]}"
                ),
                source=data / "pull-3" / "trade-quote-dte7" / symbol,
                venue_dataset="ThetaData Options / OPRA",
                symbol=symbol,
                asset_class="US listed options",
                schema="trade_quote",
                granularity="every selected trade paired with the prevailing NBBO",
                partitioning="one file or explicit empty marker per exchange date",
                timestamp_profile="thetadata-ms-et-to-ns-utc",
                scope=f"DTE <= 7; strike_range={strike_ranges[symbol]} around spot",
                description=(
                    f"ThetaData signed-flow source for {symbol}; valid_for_volume flags exclude "
                    "cancel/late-report conditions used by the ingestion plan."
                ),
                expected_start="2020-01-01",
                tags=("OPRA", "options", "tick", "trade-quote", "raw-normalized-parquet"),
            )
        )
    specs.extend(
        [
            DatasetSpec(
                provider="thetadata-opra",
                archive_name="opra__vix-options__open-interest__dte60-full-chain",
                source=data / "pull-4/open-interest/VIX",
                venue_dataset="ThetaData Options / OPRA",
                symbol="VIX",
                asset_class="US listed index options",
                schema="open_interest",
                granularity="one open-interest observation per contract per exchange date",
                partitioning="one file or explicit empty marker per exchange date",
                timestamp_profile="thetadata-ms-et-to-ns-utc",
                scope="full chain, DTE <= 60",
                description="ThetaData VIX options open-interest surface.",
                expected_start="2020-01-01",
                tags=("OPRA", "VIX", "options", "raw-normalized-parquet"),
            ),
            DatasetSpec(
                provider="thetadata-opra",
                archive_name="opra__vix-options__quote-1m__dte60-full-chain",
                source=data / "pull-4/quote-dte60-full-chain/VIX",
                venue_dataset="ThetaData Options / OPRA",
                symbol="VIX",
                asset_class="US listed index options",
                schema="quote",
                granularity="one-minute NBBO snapshots per contract",
                partitioning="one file or explicit empty marker per exchange date",
                timestamp_profile="thetadata-ms-et-to-ns-utc",
                scope="full chain, DTE <= 60, no strike filter",
                description="ThetaData VIX one-minute option quote surface.",
                expected_start="2020-01-01",
                tags=("OPRA", "VIX", "options", "intraday", "raw-normalized-parquet"),
            ),
        ]
    )
    return specs


def free_source_specs(source_root: Path) -> list[DatasetSpec]:
    data = source_root / "data"
    return [
        DatasetSpec(
            "free-sources", "yahoo__cash-daily__raw", data / "market-dependencies/raw/yahoo/daily",
            "Yahoo Finance", "QQQ,SPY,NDX,SPX", "cash equity/index", "daily_ohlcv",
            "daily source records", "one file per symbol", "date-only",
            "raw vendor responses", "Unmodified Yahoo daily-history CSV responses.", tags=("raw", "spot"),
        ),
        DatasetSpec(
            "free-sources", "yahoo__cash-daily__normalized", data / "market-dependencies/normalized/cash-daily",
            "Yahoo Finance", "QQQ,SPY,NDX,SPX", "cash equity/index", "daily_ohlcv",
            "daily OHLCV observations", "one file per symbol", "date-only",
            "normalized companion to the raw Yahoo files", "Normalized cash daily history.", tags=("normalized", "spot"),
        ),
        DatasetSpec(
            "free-sources", "yahoo__corporate-actions__normalized", data / "market-dependencies/normalized/corporate-actions",
            "Yahoo Finance", "QQQ,SPY", "ETF corporate actions", "corporate_actions",
            "dividend/split event", "one file per symbol", "mixed-free-source",
            "all available actions", "Normalized QQQ and SPY dividend/split history.", tags=("normalized", "actions"),
        ),
        DatasetSpec(
            "free-sources", "fred__usd-rates__raw", data / "market-dependencies/raw/fred",
            "FRED", "USD rates", "macro/rates", "observations",
            "source observation cadence", "one JSON response per series", "date-only",
            "DFF, SOFR, Treasury bill and constant-maturity series", "Raw FRED API responses for option-rate inputs.", tags=("raw", "rates"),
        ),
        DatasetSpec(
            "free-sources", "fred__usd-rates__normalized", data / "market-dependencies/normalized/rates",
            "FRED", "USD rates", "macro/rates", "observations",
            "daily/series-native observations", "single combined Parquet", "date-only",
            "normalized USD rate table", "Normalized rate observations for option valuation.", tags=("normalized", "rates"),
        ),
        DatasetSpec(
            "free-sources", "cboe__vx-futures__raw", data / "market-dependencies/raw/cboe",
            "Cboe", "VX", "volatility futures", "daily_futures",
            "daily OHLC, settlement, volume, and open interest per contract", "one CSV per contract expiration", "date-only",
            "official Cboe archive from 2020 onward", "Raw official Cboe VX futures contract files.", tags=("raw", "volatility"),
        ),
        DatasetSpec(
            "free-sources", "cboe__vx-futures__normalized", data / "market-dependencies/normalized/vx-futures",
            "Cboe", "VX", "volatility futures", "daily_futures",
            "daily OHLC, settlement, volume, and open interest per contract", "single combined Parquet", "date-only",
            "official Cboe archive from 2020 onward", "Normalized VX term-structure table retaining monthly/weekly identifiers.", tags=("normalized", "volatility"),
        ),
        DatasetSpec(
            "free-sources", "federal-reserve__fomc-pages__raw", data / "external-context/raw/federal-reserve",
            "Federal Reserve", "FOMC", "event calendar", "HTML pages",
            "meeting schedule page", "one file per source page/year", "date-only",
            "historical/current meeting calendars", "Raw Federal Reserve FOMC calendar pages.", tags=("raw", "events"),
        ),
        DatasetSpec(
            "free-sources", "fred__volatility-and-releases__raw", data / "external-context/raw/fred",
            "FRED", "VIX,VXN,VIX3M,economic releases", "volatility/macro", "JSON responses",
            "source observation cadence", "one JSON response per series/release", "date-only",
            "free external context", "Raw FRED volatility-index and release responses.", tags=("raw", "volatility", "events"),
        ),
        DatasetSpec(
            "free-sources", "cboe__vvix__raw", data / "external-context/raw/cboe",
            "Cboe", "VVIX", "volatility index", "daily_history",
            "daily observations", "single CSV", "date-only",
            "available official history", "Raw official Cboe VVIX history.", tags=("raw", "volatility"),
        ),
        DatasetSpec(
            "free-sources", "context__volatility__normalized", data / "external-context/normalized/volatility",
            "Cboe/FRED", "VIX,VXN,VIX3M,VVIX", "volatility indices", "daily_history",
            "daily observations", "one Parquet per index/source", "date-only",
            "normalized free-source volatility context", "Normalized cash volatility indices.", tags=("normalized", "volatility"),
        ),
        DatasetSpec(
            "free-sources", "context__event-calendar__normalized", data / "external-context/normalized/events",
            "Federal Reserve/FRED/market calendars", "market events", "event calendar", "event_calendar",
            "one row per event/session", "small topical Parquet files", "mixed-free-source",
            "FOMC, economic releases, earnings, and market sessions", "Normalized event calendar tables.", tags=("normalized", "events"),
        ),
        DatasetSpec(
            "free-sources", "context__earnings__normalized", data / "external-context/normalized/earnings",
            "free calendar sources", "mega-cap equities", "earnings calendar", "earnings",
            "one row per earnings event", "one Parquet per symbol", "mixed-free-source",
            "tracked mega-cap constituents", "Normalized earnings dates used as event context.", tags=("normalized", "events", "earnings"),
        ),
    ]


def legacy_free_source_specs(legacy_root: Path) -> list[DatasetSpec]:
    """Preserve the useful context already present on the RunPod volume."""
    context = legacy_root / "context"
    common = {
        "provider": "free-sources",
        "asset_class": "cross-asset context",
        "timestamp_profile": "mixed-free-source",
        "status": "complete",
        "adjustment": "retained exactly as previously acquired",
        "tags": ("legacy-source-tree", "context"),
    }
    rows = [
        (
            "nasdaq__trading-calendars__reference",
            legacy_root / "calendars",
            "Nasdaq/reference sources",
            "US market calendars",
            "PDF/HTML reference",
            "annual trading-calendar documents",
            "one file per calendar year/source",
            "2020-2025 reference calendars",
            "Original market-calendar reference documents.",
            ("*",),
        ),
        (
            "fred__rates__legacy-raw",
            context / "fred_rates_v1",
            "FRED",
            "USD rates",
            "JSON responses and provenance",
            "source observation cadence",
            "one response per FRED series",
            "previously acquired rate inputs",
            "Legacy raw FRED rate responses with receipt and SHA-256 manifest.",
            ("*",),
        ),
        (
            "fred__volatility-indices__legacy",
            context / "vol_indices",
            "FRED",
            "VIX,VXD,RVX",
            "daily history",
            "daily observations",
            "one CSV per index",
            "available source history",
            "Legacy FRED cash volatility-index histories.",
            ("*",),
        ),
        (
            "cross-asset__rates",
            context / "asset_port_data/rates",
            "FRED",
            "USD rates",
            "daily history",
            "daily observations",
            "one CSV per series plus manifest",
            "cross-asset model inputs",
            "Rate series from the legacy cross-asset context pull.",
            ("*",),
        ),
        (
            "cross-asset__nikkei-and-fx",
            context / "asset_port_data/nikkei",
            "FRED/Sina",
            "Nikkei,NKD,USDJPY",
            "mixed daily/intraday history",
            "source-native daily or intraday observations",
            "one CSV per instrument plus manifest",
            "cross-asset Nikkei context",
            "Nikkei index/futures/FX context and provenance.",
            ("*",),
        ),
        (
            "cross-asset__copper",
            context / "asset_port_data/copper",
            "FRED/Sina/SHFE comparison",
            "HG,SHFE copper,USDCNY",
            "mixed daily and 1/5/15/30/60-minute history",
            "source-native interval stated in each filename",
            "one CSV per instrument/interval plus manifest",
            "cross-asset copper context",
            "COMEX/SHFE copper, FX, and verification context.",
            ("*",),
        ),
        (
            "cross-asset__acquisition-metadata",
            context / "asset_port_data",
            "legacy ingestion scripts/logs",
            "cross-asset context",
            "provenance",
            "one record per acquisition run",
            "root-level files only",
            "metadata for the Nikkei/copper/rates context pull",
            "Legacy fetch logs, notes, and acquisition script.",
            ("fetch_log*.json", "fetch_akshare.py", "MANIFEST_NOTES.txt"),
        ),
        (
            "yahoo__commodity-futures-daily__legacy",
            context,
            "Yahoo Finance",
            "SI,HG,NKD,GC",
            "daily futures history",
            "daily OHLCV observations",
            "one CSV per continuous Yahoo symbol",
            "legacy cross-asset daily context",
            "Yahoo daily futures histories retained from the earlier archive.",
            ("yahoo_*.csv",),
        ),
        (
            "ishares__slv-fund-flows",
            context / "slv",
            "iShares",
            "SLV",
            "fund NAV/shares/ounces",
            "daily observations",
            "CSV plus raw workbook and manifest",
            "available fund history",
            "SLV NAV, shares, and implied ounces-flow context.",
            ("*",),
        ),
        (
            "shfe__metal-inventories",
            context / "shfe_inventory",
            "SHFE/secondary mirrors",
            "silver,copper",
            "inventory history",
            "daily or weekly observations by file",
            "one CSV per metal/frequency plus manifest",
            "available source history",
            "SHFE silver and copper inventory context.",
            ("*",),
        ),
        (
            "fred__macro-context__legacy-refresh",
            context / "fred_refresh",
            "FRED",
            "USDJPY,GVZ,DGS10,T10YIE,dollar index",
            "daily macro history",
            "daily/source-native observations",
            "one CSV per series plus manifest",
            "legacy macro refresh",
            "Additional FRED macro and cross-asset context.",
            ("*",),
        ),
        (
            "cftc__commitments-of-traders",
            context / "cot",
            "CFTC",
            "futures positioning",
            "legacy/disaggregated/TFF reports",
            "weekly reports",
            "annual TXT/ZIP files plus manifests",
            "2021-2026",
            "CFTC Commitments of Traders source reports.",
            ("*",),
        ),
        (
            "central-banks__fomc-and-boj-calendars",
            context,
            "Federal Reserve/Bank of Japan",
            "FOMC,BOJ",
            "event calendar",
            "one row per scheduled event",
            "two CSV files",
            "available event history",
            "Legacy FOMC and BOJ event calendars.",
            ("calendar_*.csv",),
        ),
        (
            "bls__release-calendars",
            context / "bls_calendar",
            "US Bureau of Labor Statistics/Wayback",
            "CPI,employment releases",
            "release calendar and source snapshots",
            "one row/page per release calendar artifact",
            "CSV/HTML and provenance",
            "available historical release calendars",
            "BLS CPI and employment-release calendars with archived source pages.",
            ("*",),
        ),
    ]
    specs: list[DatasetSpec] = []
    for (
        archive_name, source, venue_dataset, symbol, schema, granularity,
        partitioning, scope, description, include_patterns,
    ) in rows:
        specs.append(
            DatasetSpec(
                provider=common["provider"],
                archive_name=archive_name,
                source=source,
                venue_dataset=venue_dataset,
                symbol=symbol,
                asset_class=common["asset_class"],
                schema=schema,
                granularity=granularity,
                partitioning=partitioning,
                timestamp_profile=common["timestamp_profile"],
                scope=scope,
                description=description,
                status=common["status"],
                adjustment=common["adjustment"],
                tags=common["tags"],
                include_patterns=include_patterns,
            )
        )
    return specs


def derived_specs(source_root: Path) -> list[DatasetSpec]:
    return [
        DatasetSpec(
            provider="derived",
            archive_name="continuous-futures__instrument-and-roll-maps",
            source=source_root / "data/derived/futures-rolls",
            venue_dataset="derived from QuantPad GLBX.MDP3",
            symbol="NQ.c.0,ES.c.0,YM.c.0",
            asset_class="continuous futures metadata",
            schema="instrument_map and roll_segments",
            granularity="one row per instrument or continuous-contract segment",
            partitioning="one pair of files per futures root",
            timestamp_profile="continuous-roll-map-mixed-utc",
            scope="full bar/definition coverage for NQ, ES, and YM",
            description="Auditable maps from continuous instrument IDs to raw contracts and roll segments; RTY is omitted because its older definitions were intentionally skipped.",
            known_gaps=("RTY roll maps intentionally omitted because RTY definitions are incomplete.",),
            tags=("derived", "symbology", "rolls"),
            include_patterns=("nq-*", "es-*", "ym-*"),
        )
    ]


def all_specs(source_root: Path, legacy_root: Path) -> list[DatasetSpec]:
    return (
        quantpad_specs(source_root)
        + databento_specs(source_root)
        + legacy_databento_specs(legacy_root)
        + theta_specs(source_root)
        + free_source_specs(source_root)
        + legacy_free_source_specs(legacy_root)
        + derived_specs(source_root)
    )


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    partial.write_text(value, encoding="utf-8")
    os.replace(partial, path)


def atomic_json(path: Path, value: Any) -> None:
    atomic_text(path, json.dumps(value, indent=2, sort_keys=True, default=str) + "\n")


def completed_source_files(root: Path, include_patterns: tuple[str, ...] = ("*",)) -> list[Path]:
    if not root.exists():
        return []
    excluded_suffixes = (".part", ".tmp", ".lock", ".crdownload")
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not path.name.startswith(".")
        and not path.name.endswith(excluded_suffixes)
        and any(fnmatch.fnmatch(path.name, pattern) for pattern in include_patterns)
    )


def source_label(path: Path, source_root: Path) -> str:
    try:
        return str(path.relative_to(source_root))
    except ValueError:
        return str(path)


def file_format(path: Path) -> str:
    lower = path.name.lower()
    if lower.endswith(".dbn.zst"):
        return "dbn.zst"
    if lower.endswith(".empty.json"):
        return "empty-marker.json"
    if "." not in path.name:
        return "unknown"
    return lower.rsplit(".", 1)[1]


def partition_key(path: Path) -> str | None:
    name = path.name
    patterns = (
        r"(20\d{2}-\d{2}-\d{2})",
        r"(20\d{2}-\d{2})",
        r"((?:19|20)\d{6})",
        r"((?:19|20)\d{2})",
    )
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            value = match.group(1)
            if len(value) == 8 and "-" not in value:
                return f"{value[:4]}-{value[4:6]}-{value[6:]}"
            return value
    return None


def jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if hasattr(value, "isoformat"):
        try:
            return value.isoformat()
        except Exception:
            pass
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def epoch_to_iso(value: Any, unit: str) -> str | None:
    try:
        number = int(value)
    except (TypeError, ValueError, OverflowError):
        return None
    divisor = 1_000_000_000 if unit == "nanoseconds" else 1_000
    try:
        return datetime.fromtimestamp(number / divisor, tz=UTC).isoformat()
    except (OSError, OverflowError, ValueError):
        return None


def parquet_details(path: Path, profile_id: str) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    metadata = parquet.metadata
    arrow_schema = parquet.schema_arrow
    fields = [{"name": field.name, "type": str(field.type), "nullable": field.nullable} for field in arrow_schema]
    candidates = (
        "ts_event", "t", "trade_date", "date", "request_date", "segment_start_ts_utc",
    )
    primary = next((name for name in candidates if name in arrow_schema.names), None)
    minimum: Any = None
    maximum: Any = None
    if primary is not None:
        index = arrow_schema.names.index(primary)
        for row_group_index in range(metadata.num_row_groups):
            column = metadata.row_group(row_group_index).column(index)
            stats = column.statistics
            if stats is None or not stats.has_min_max:
                continue
            low, high = stats.min, stats.max
            if minimum is None or low < minimum:
                minimum = low
            if maximum is None or high > maximum:
                maximum = high
    profile = TIMESTAMP_PROFILES[profile_id]
    unit = profile.get("stored_unit")
    if primary == "t" and unit in {"nanoseconds", "milliseconds"}:
        minimum = epoch_to_iso(minimum, unit) if minimum is not None else None
        maximum = epoch_to_iso(maximum, unit) if maximum is not None else None
    else:
        minimum = jsonable(minimum)
        maximum = jsonable(maximum)
    return {
        "rows": metadata.num_rows,
        "row_groups": metadata.num_row_groups,
        "schema_fields": fields,
        "primary_time_field": primary,
        "observed_time_min": minimum,
        "observed_time_max": maximum,
    }


def monthly_keys(start: str, end: str) -> list[str]:
    year, month = (int(part) for part in start.split("-"))
    end_year, end_month = (int(part) for part in end.split("-"))
    values: list[str] = []
    while (year, month) <= (end_year, end_month):
        values.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            month = 1
            year += 1
    return values


def flattened_destination(source_file: Path, source_root: Path, used: set[str]) -> str:
    candidate = source_file.name
    if candidate not in used:
        used.add(candidate)
        return candidate
    relative = source_file.relative_to(source_root)
    prefix = "__".join(relative.parts[:-1])
    candidate = f"{prefix}__{source_file.name}" if prefix else source_file.name
    suffix = 2
    original = candidate
    while candidate in used:
        candidate = f"{original}__{suffix}"
        suffix += 1
    used.add(candidate)
    return candidate


def hardlink(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if os.path.samefile(source, destination):
            return
        raise FileExistsError(f"Refusing to replace unrelated staged file: {destination}")
    try:
        os.link(source, destination)
    except OSError as error:
        if error.errno == errno.EXDEV:
            raise RuntimeError(
                f"Source and stage roots are on different filesystems; hard-link staging is unsafe: {source}"
            ) from error
        raise


def stage_archive(
    source_root: Path,
    legacy_root: Path,
    stage_root: Path,
    dry_run: bool = False,
) -> dict[str, Any]:
    manifests = stage_root / "manifests"
    specs = all_specs(source_root, legacy_root)
    file_rows: list[dict[str, Any]] = []
    catalog: list[dict[str, Any]] = []
    schema_catalog: dict[str, list[dict[str, Any]]] = {}
    omitted_empty_specs: list[str] = []

    for spec in specs:
        source_files = completed_source_files(spec.source, spec.include_patterns)
        if not source_files:
            omitted_empty_specs.append(spec.dataset_id)
            continue
        dataset_path = stage_root / spec.provider / spec.archive_name
        used_names: set[str] = set()
        dataset_rows = 0
        known_row_files = 0
        dataset_bytes = 0
        observed_minima: list[str] = []
        observed_maxima: list[str] = []
        partition_keys: list[str] = []
        formats: set[str] = set()
        distinct_schemas: dict[str, list[dict[str, Any]]] = {}
        empty_markers = 0
        unreadable: list[dict[str, str]] = []

        for source_file in source_files:
            destination_name = (
                flattened_destination(source_file, spec.source, used_names)
                if spec.flatten
                else str(source_file.relative_to(spec.source))
            )
            destination = dataset_path / destination_name
            if not dry_run:
                hardlink(source_file, destination)
            fmt = file_format(source_file)
            formats.add(fmt)
            size = source_file.stat().st_size
            dataset_bytes += size
            key = partition_key(source_file)
            if key:
                partition_keys.append(key)
            detail: dict[str, Any] = {
                "rows": 0 if fmt == "empty-marker.json" else None,
                "row_groups": None,
                "primary_time_field": None,
                "observed_time_min": None,
                "observed_time_max": None,
            }
            if fmt == "empty-marker.json":
                empty_markers += 1
            elif fmt == "parquet":
                try:
                    detail = parquet_details(source_file, spec.timestamp_profile)
                    dataset_rows += int(detail["rows"])
                    known_row_files += 1
                    fields = detail.pop("schema_fields")
                    schema_key = json.dumps(fields, sort_keys=True)
                    distinct_schemas[schema_key] = fields
                    if detail["observed_time_min"] is not None:
                        observed_minima.append(str(detail["observed_time_min"]))
                    if detail["observed_time_max"] is not None:
                        observed_maxima.append(str(detail["observed_time_max"]))
                except Exception as error:
                    unreadable.append({"file": str(source_file), "error": f"{type(error).__name__}: {error}"})
            file_rows.append(
                {
                    "provider": spec.provider,
                    "dataset_id": spec.dataset_id,
                    "archive_path": str(destination.relative_to(stage_root)),
                    "source_path": source_label(source_file, source_root),
                    "format": fmt,
                    "bytes": size,
                    "rows": detail["rows"],
                    "row_groups": detail["row_groups"],
                    "partition_key": key,
                    "primary_time_field": detail["primary_time_field"],
                    "observed_time_min": detail["observed_time_min"],
                    "observed_time_max": detail["observed_time_max"],
                    "mtime_utc": datetime.fromtimestamp(source_file.stat().st_mtime, tz=UTC).isoformat(),
                }
            )

        status = spec.status
        gaps = list(spec.known_gaps)
        missing_months: list[str] = []
        if spec.schema == "mbp-1" and spec.expected_start:
            current_month = datetime.now(tz=UTC).strftime("%Y-%m")
            present = {key for key in partition_keys if key and len(key) == 7}
            missing_months = sorted(set(monthly_keys(spec.expected_start, current_month)) - present)
            if missing_months and status == "complete":
                status = "incomplete"
                gaps.append("Missing monthly partitions detected by the archive builder.")

        dataset_entry = {
            **asdict(spec),
            "source": source_label(spec.source, source_root),
            "dataset_id": spec.dataset_id,
            "archive_path": str(dataset_path.relative_to(stage_root)),
            "status": status,
            "known_gaps": gaps,
            "missing_months": missing_months,
            "file_count": len(source_files),
            "empty_marker_count": empty_markers,
            "total_bytes": dataset_bytes,
            "total_rows": dataset_rows if known_row_files else None,
            "files_with_known_row_count": known_row_files,
            "formats": sorted(formats),
            "partition_min": min(partition_keys) if partition_keys else None,
            "partition_max": max(partition_keys) if partition_keys else None,
            "observed_time_min": min(observed_minima) if observed_minima else None,
            "observed_time_max": max(observed_maxima) if observed_maxima else None,
            "timestamp_semantics": TIMESTAMP_PROFILES[spec.timestamp_profile],
            "unreadable_files": unreadable,
        }
        catalog.append(dataset_entry)
        schema_catalog[spec.dataset_id] = list(distinct_schemas.values())

    source_partials = [
        {
            "source_path": str(path.relative_to(source_root)),
            "bytes": path.stat().st_size,
            "reason": "incomplete atomic download; excluded from archive",
        }
        for path in sorted((source_root / "data").rglob("*.part"))
    ]
    explicit_exclusions = []
    for relative, reason in (
        (
            Path("data/phase-3/glbx-mdp3/nq-c-0/mbp-10"),
            "NQ MBP-10 was declared unnecessary and is intentionally excluded.",
        ),
        (
            Path("data/phase-4/glbx-mdp3/nq-c-0/mbp-1-yearly"),
            "Superseded/benchmark yearly NQ MBP-1 copies are excluded to avoid duplicating the complete monthly raw archive.",
        ),
    ):
        directory = source_root / relative
        files = completed_source_files(directory)
        explicit_exclusions.append(
            {
                "source_path": str(relative),
                "file_count": len(files),
                "bytes": sum(path.stat().st_size for path in files),
                "reason": reason,
            }
        )
    exclusions = {
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "source_partials": source_partials,
        "explicit_exclusions": explicit_exclusions,
        "empty_dataset_specs_omitted": omitted_empty_specs,
        "always_excluded": ["API keys and .env files", "temporary files", "process logs", "virtual environments"],
    }
    summary = {
        "archive_version": 1,
        "generated_at": datetime.now(tz=UTC).isoformat(),
        "source_root": str(source_root),
        "legacy_source_root": str(legacy_root),
        "archive_root": str(stage_root),
        "layout": "provider/dataset/files; dataset files are flattened where names are unique",
        "storage_method": "hard links to immutable completed source files; byte-identical and no additional disk copy",
        "providers": sorted({entry["provider"] for entry in catalog}),
        "dataset_count": len(catalog),
        "file_count": len(file_rows),
        "total_bytes": sum(int(row["bytes"]) for row in file_rows),
        "known_parquet_rows": sum(int(row["rows"] or 0) for row in file_rows),
        "unreadable_parquet_files": sum(len(entry["unreadable_files"]) for entry in catalog),
        "excluded_partial_files": len(source_partials),
        "remote_target": DEFAULT_REMOTE,
    }

    if dry_run:
        return {"summary": summary, "catalog": catalog, "exclusions": exclusions}

    catalog.sort(key=lambda item: item["dataset_id"])
    file_rows.sort(key=lambda item: item["archive_path"])
    atomic_json(manifests / "archive-summary.json", summary)
    atomic_json(manifests / "dataset-catalog.json", {"archive": summary, "datasets": catalog})
    atomic_json(manifests / "schema-catalog.json", schema_catalog)
    atomic_json(manifests / "timestamp-conventions.json", TIMESTAMP_PROFILES)
    atomic_json(manifests / "exclusions-and-gaps.json", exclusions)
    source_roll_manifest = source_root / "manifests/futures-roll-map.json"
    if source_roll_manifest.is_file():
        atomic_text(
            manifests / "source-futures-roll-map.json",
            source_roll_manifest.read_text(encoding="utf-8"),
        )
    legacy_readme = legacy_root / "README.md"
    if legacy_readme.is_file():
        atomic_text(
            manifests / "legacy-source-readme.md",
            legacy_readme.read_text(encoding="utf-8"),
        )

    dataset_csv_path = manifests / "datasets.csv"
    dataset_csv_rows = []
    for entry in catalog:
        dataset_csv_rows.append(
            {
                key: json.dumps(value, sort_keys=True) if isinstance(value, (dict, list, tuple)) else value
                for key, value in entry.items()
                if key not in {"timestamp_semantics", "unreadable_files"}
            }
        )
    write_csv(dataset_csv_path, dataset_csv_rows)
    write_csv(manifests / "files.csv", file_rows)
    table = pa.Table.from_pylist(file_rows)
    partial = manifests / "files.parquet.part"
    pq.write_table(table, partial, compression="zstd")
    os.replace(partial, manifests / "files.parquet")
    atomic_text(manifests / "README.md", render_readme(summary, catalog))
    return {"summary": summary, "catalog": catalog, "exclusions": exclusions}


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        atomic_text(path, "")
        return
    partial = path.with_suffix(path.suffix + ".part")
    with partial.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    os.replace(partial, path)


def render_readme(summary: dict[str, Any], catalog: list[dict[str, Any]]) -> str:
    lines = [
        "# Market data archive",
        "",
        "This is a shallow, model-readable view of the acquired market data. Raw records are",
        "not combined, resampled, adjusted, or rewritten. Completed source files are staged",
        "byte-for-byte via hard links before upload.",
        "",
        "## Layout",
        "",
        "- `quantpad/`: Databento CME and limited OPRA reference data routed through QuantPad.",
        "- `databento/`: CME options-on-futures archives purchased directly from Databento.",
        "- `thetadata-opra/`: Primary OPRA options archive acquired through ThetaData.",
        "- `free-sources/`: Cboe, FRED, Yahoo, Federal Reserve, and calendar context.",
        "- `derived/`: Auditable continuous-futures instrument and roll maps.",
        "- `manifests/`: Machine-readable inventory, schemas, timestamp conventions, and gaps.",
        "",
        "Each provider folder is flat: every immediate child is one self-describing dataset,",
        "and partition files are directly inside that dataset folder.",
        "",
        "## Start here",
        "",
        "1. `dataset-catalog.json` — semantic inventory with granularity, scope, coverage,",
        "   timestamp semantics, completeness, row counts, sizes, and known gaps.",
        "2. `files.parquet` or `files.csv` — exact per-file inventory and observed time bounds.",
        "3. `schema-catalog.json` — Arrow schemas observed in every Parquet dataset.",
        "4. `timestamp-conventions.json` — units, precision, time zones, and DST conversion.",
        "5. `exclusions-and-gaps.json` — incomplete parts, intentionally skipped data, and",
        "   superseded duplicates.",
        "",
        "## Timestamp warning",
        "",
        "QuantPad tick/event schemas use integer UTC nanoseconds, while its OHLCV bars use",
        "integer UTC milliseconds. Direct Databento files remain native DBN with nanosecond",
        "timestamps. ThetaData originally supplies millisecond wall times in America/New_York;",
        "the ingestion code localized them with DST rules and stored UTC Arrow timestamps at",
        "nanosecond type width but millisecond effective precision. Never infer units solely",
        "from the integer/timestamp container—use each dataset's timestamp profile.",
        "",
        "## Archive totals",
        "",
        f"- Datasets: {summary['dataset_count']}",
        f"- Files: {summary['file_count']}",
        f"- Bytes: {summary['total_bytes']}",
        f"- Known Parquet rows: {summary['known_parquet_rows']}",
        f"- Excluded incomplete files: {summary['excluded_partial_files']}",
        "",
        "## Dataset index",
        "",
        "| Dataset | Status | Granularity | Partitions | Rows | Bytes |",
        "|---|---|---|---:|---:|---:|",
    ]
    for entry in sorted(catalog, key=lambda item: item["dataset_id"]):
        rows = "unknown" if entry["total_rows"] is None else str(entry["total_rows"])
        lines.append(
            f"| `{entry['dataset_id']}` | {entry['status']} | {entry['granularity']} | "
            f"{entry['file_count']} | {rows} | {entry['total_bytes']} |"
        )
    lines.extend(["", "Generated at " + summary["generated_at"] + ".", ""])
    return "\n".join(lines)


def pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def wait_for_pids(pids: Iterable[int], poll_seconds: int = 30) -> None:
    pending = set(pids)
    while pending:
        pending = {pid for pid in pending if pid_alive(pid)}
        if pending:
            print(json.dumps({"status": "waiting", "pids": sorted(pending)}), flush=True)
            time.sleep(poll_seconds)


def run_checked(command: list[str], log_path: Path | None = None) -> None:
    if log_path is None:
        subprocess.run(command, check=True)
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        subprocess.run(command, check=True, stdout=handle, stderr=subprocess.STDOUT)


def upload_archive(stage_root: Path, config: Path, remote: str, log_root: Path) -> dict[str, Any]:
    if not config.is_file():
        raise FileNotFoundError(f"rclone config is missing: {config}")
    copy_log = log_root / "r2-upload.log"
    check_log = log_root / "r2-check.log"
    base = ["rclone", "--config", str(config)]
    copy_command = base + [
        "copy", str(stage_root), remote,
        "--transfers", "64", "--checkers", "64", "--fast-list",
        "--retries", "12", "--low-level-retries", "20",
        "--contimeout", "30s", "--timeout", "10m",
        "--stats", "30s", "--stats-one-line", "--log-level", "INFO",
    ]
    started = datetime.now(tz=UTC)
    run_checked(copy_command, copy_log)
    check_command = base + [
        "check", str(stage_root), remote,
        "--checkers", "64", "--one-way", "--size-only",
        "--combined", str(log_root / "r2-check-differences.txt"),
        "--log-level", "INFO",
    ]
    run_checked(check_command, check_log)
    report = {
        "status": "complete",
        "started_at": started.isoformat(),
        "completed_at": datetime.now(tz=UTC).isoformat(),
        "source": str(stage_root),
        "destination": remote,
        "transfers": 64,
        "checkers": 64,
        "verification": "rclone check --one-way --size-only",
        "copy_log": str(copy_log),
        "check_log": str(check_log),
    }
    atomic_json(stage_root / "manifests/r2-upload-report.json", report)
    run_checked(
        base + [
            "copy", str(stage_root / "manifests"), f"{remote}/manifests",
            "--transfers", "64", "--checkers", "64", "--fast-list",
        ],
        copy_log,
    )
    return report


def validate_roll_outputs(source_root: Path) -> None:
    directory = source_root / "data/derived/futures-rolls"
    expected = {
        f"{root}-{kind}.parquet"
        for root in (root.lower() for root in ROLL_MAP_ROOTS)
        for kind in ("instruments", "rolls")
    }
    present = {path.name for path in directory.glob("*.parquet")}
    missing = sorted(expected - present)
    if missing:
        raise RuntimeError(f"Roll-map build did not produce: {', '.join(missing)}")
    for path in sorted(directory.glob("*.parquet")):
        metadata = pq.ParquetFile(path).metadata
        if metadata.num_rows == 0:
            raise RuntimeError(f"Roll-map output has zero rows: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("stage", "upload", "run"))
    parser.add_argument("--source-root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--legacy-root", type=Path, default=DEFAULT_LEGACY_ROOT)
    parser.add_argument("--stage-root", type=Path, default=DEFAULT_STAGE_ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_RCLONE_CONFIG)
    parser.add_argument("--remote", default=DEFAULT_REMOTE)
    parser.add_argument("--wait-pid", type=int, action="append", default=[])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    source_root = args.source_root.resolve()
    legacy_root = args.legacy_root.resolve()
    stage_root = args.stage_root.resolve()
    log_root = source_root / "logs"

    if args.wait_pid:
        wait_for_pids(args.wait_pid)
    if args.command == "run":
        build_command = ["uv", "run", "python", "build_futures_roll_map.py"]
        for root in ROLL_MAP_ROOTS:
            build_command.extend(("--root", root))
        run_checked(build_command, log_root / "build-futures-roll-map.log")
        validate_roll_outputs(source_root)
    result: dict[str, Any] = {}
    if args.command in {"stage", "run"}:
        result["stage"] = stage_archive(
            source_root,
            legacy_root,
            stage_root,
            dry_run=args.dry_run,
        )["summary"]
    if args.command in {"upload", "run"} and not args.dry_run:
        result["upload"] = upload_archive(stage_root, args.config, args.remote, log_root)
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
