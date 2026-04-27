#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from urllib import request


def post_json(base_url: str, path: str, payload: dict, headers: dict[str, str] | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{base_url}{path}",
        data=body,
        method="POST",
        headers={"content-type": "application/json", **(headers or {})},
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(base_url: str, path: str, headers: dict[str, str] | None = None) -> dict | list:
    req = request.Request(
        f"{base_url}{path}",
        method="GET",
        headers=headers or {},
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Pulse AI demo replay and print summary.")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--workspace-id", default="default", help="Workspace id for replay")
    parser.add_argument("--source", default="demo-stream", help="Source for replayed events")
    parser.add_argument("--signal-type", default="latency", help="Signal type")
    parser.add_argument("--entity-id", default="entity-demo-1", help="Entity id")
    parser.add_argument("--count", type=int, default=120, help="Replay event count")
    parser.add_argument("--seed", type=int, default=42, help="Replay seed")
    parser.add_argument("--spike-every", type=int, default=12, help="Inject spike every N events")
    args = parser.parse_args()

    replay_payload = {
        "workspace_id": args.workspace_id,
        "source": args.source,
        "event_type": args.signal_type,
        "signal_type": args.signal_type,
        "entity_id": args.entity_id,
        "count": args.count,
        "seed": args.seed,
        "inject_spike_every": args.spike_every,
    }
    replay = post_json(args.base_url, "/api/v1/events/replay", replay_payload)
    summary = get_json(args.base_url, "/api/v1/metrics/summary")
    scored = get_json(args.base_url, "/api/v1/events/scored?limit=10&anomalous_only=true")

    print("\n=== Pulse AI Demo Replay ===")
    print(json.dumps(replay, indent=2))
    print("\n=== Metrics Summary ===")
    print(json.dumps(summary, indent=2))
    print("\n=== Top Anomalies (latest 10) ===")
    print(json.dumps(scored, indent=2))


if __name__ == "__main__":
    main()
