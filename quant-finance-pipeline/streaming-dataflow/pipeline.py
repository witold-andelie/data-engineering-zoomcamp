#!/usr/bin/env python3
"""Dataflow streaming pipeline: Pub/Sub -> BigQuery."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Tuple

import apache_beam as beam
from apache_beam.io import ReadFromPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows


BQ_SCHEMA = (
    "event_time:TIMESTAMP,"
    "symbol:STRING,"
    "price:FLOAT,"
    "quantity:FLOAT,"
    "source:STRING,"
    "ingestion_mode:STRING,"
    "trade_id:STRING,"
    "side:STRING"
)


class ParseTradeEvent(beam.DoFn):
    def process(self, element: bytes) -> Iterable[Dict[str, Any]]:
        try:
            raw = json.loads(element.decode("utf-8"))
            event_time = raw.get("event_time")
            if not event_time:
                raise ValueError("event_time missing")

            # Accept ISO string; normalize timezone if naive.
            parsed = datetime.fromisoformat(event_time.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            yield {
                "event_time": parsed.isoformat(),
                "symbol": str(raw["symbol"]).upper(),
                "price": float(raw["price"]),
                "quantity": float(raw["quantity"]),
                "source": str(raw.get("source", "unknown")),
                "ingestion_mode": str(raw.get("ingestion_mode", "stream")),
                "trade_id": str(raw["trade_id"]) if raw.get("trade_id") is not None else None,
                "side": raw.get("side"),
            }
        except Exception as exc:  # noqa: BLE001
            logging.warning("Drop bad record: %s ; err=%s", element[:200], exc)


class ValidateRequiredFields(beam.DoFn):
    REQUIRED = ("event_time", "symbol", "price", "quantity", "source", "ingestion_mode")

    def process(self, row: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        missing = [k for k in self.REQUIRED if row.get(k) is None]
        if missing:
            logging.warning("Drop record due to missing fields=%s row=%s", missing, row)
            return

        yield row


def _parse_known_args(argv: list[str] | None = None) -> Tuple[PipelineOptions, Dict[str, str]]:
    options = PipelineOptions(argv)
    custom = options.get_all_options()

    required = ["subscription", "output_table"]
    missing = [name for name in required if not custom.get(name)]
    if missing:
        raise ValueError(f"Missing required options: {missing}")

    return options, {"subscription": custom["subscription"], "output_table": custom["output_table"]}


def run(argv: list[str] | None = None) -> None:
    options, args = _parse_known_args(argv)

    with beam.Pipeline(options=options) as p:
        (
            p
            | "ReadPubSub" >> ReadFromPubSub(subscription=args["subscription"])
            | "ParseJSON" >> beam.ParDo(ParseTradeEvent())
            | "ValidateRequired" >> beam.ParDo(ValidateRequiredFields())
            | "Window60s" >> beam.WindowInto(FixedWindows(60))
            | "WriteBQ"
            >> WriteToBigQuery(
                table=args["output_table"],
                schema=BQ_SCHEMA,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                custom_gcs_temp_location=options.get_all_options().get("temp_location"),
            )
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run()
