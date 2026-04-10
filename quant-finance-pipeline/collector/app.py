#!/usr/bin/env python3
"""Realtime trade collector: WebSocket -> Pub/Sub (or stdout)."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict

import websockets
from google.cloud import pubsub_v1


def _env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing env var: {name}")
    return value


class Publisher:
    def __init__(self, mode: str, topic: str | None = None) -> None:
        self.mode = mode
        self.topic = topic
        self.client = pubsub_v1.PublisherClient() if mode == "pubsub" else None

    def publish(self, payload: Dict[str, Any]) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        if self.mode == "pubsub":
            if not self.client or not self.topic:
                raise RuntimeError("Pub/Sub mode requires client and topic")
            future = self.client.publish(self.topic, data=data)
            message_id = future.result(timeout=10)
            logging.debug("Published message_id=%s", message_id)
            return

        print(json.dumps(payload, ensure_ascii=False))


def map_binance_trade_event(raw: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """Map Binance trade payload to TradeEvent contract."""
    event_ts_ms = raw.get("T") or raw.get("E")
    if event_ts_ms is None:
        event_time = datetime.now(timezone.utc).isoformat()
    else:
        event_time = datetime.fromtimestamp(event_ts_ms / 1000, tz=timezone.utc).isoformat()

    return {
        "event_time": event_time,
        "symbol": symbol.upper(),
        "price": float(raw["p"]),
        "quantity": float(raw["q"]),
        "source": "binance_ws",
        "ingestion_mode": "stream",
        "trade_id": str(raw.get("t")) if raw.get("t") is not None else None,
        "side": "sell" if raw.get("m") else "buy",
    }


async def collect_loop() -> None:
    ws_base = _env("SOURCE_WS_URL", "wss://stream.binance.com:9443/ws")
    symbol = _env("SOURCE_SYMBOL", "btcusdt").lower()
    mode = _env("PUBLISH_MODE", "stdout").lower()
    topic = os.getenv("PUBSUB_TOPIC")

    if mode not in {"stdout", "pubsub"}:
        raise RuntimeError("PUBLISH_MODE must be one of: stdout, pubsub")

    if mode == "pubsub" and not topic:
        raise RuntimeError("PUBSUB_TOPIC is required when PUBLISH_MODE=pubsub")

    publisher = Publisher(mode=mode, topic=topic)
    ws_url = f"{ws_base}/{symbol}@trade"

    backoff_seconds = 1
    while True:
        try:
            logging.info("Connecting to %s", ws_url)
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as websocket:
                logging.info("Connected. Streaming symbol=%s mode=%s", symbol, mode)
                backoff_seconds = 1
                async for message in websocket:
                    raw = json.loads(message)
                    payload = map_binance_trade_event(raw, symbol=symbol)
                    publisher.publish(payload)
        except Exception as exc:  # noqa: BLE001
            logging.exception("Collector loop error: %s", exc)
            await asyncio.sleep(backoff_seconds)
            backoff_seconds = min(backoff_seconds * 2, 30)


def main() -> None:
    log_level = _env("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    asyncio.run(collect_loop())


if __name__ == "__main__":
    main()
