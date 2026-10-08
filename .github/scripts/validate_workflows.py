#!/usr/bin/env python3
"""Validate n8n workflow JSON files without depending on a heavyweight local package."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def validate_workflow(path: Path) -> None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            workflow = json.load(handle)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc.msg} (line {exc.lineno}, column {exc.colno})") from exc
    except OSError as exc:
        raise ValueError(f"unable to read file: {exc}") from exc

    if not isinstance(workflow, dict):
        raise ValueError("workflow must be a JSON object")

    if not isinstance(workflow.get("nodes"), list):
        raise ValueError("missing required 'nodes' array")

    if "connections" in workflow and not isinstance(workflow["connections"], dict):
        raise ValueError("'connections' must be an object when present")

    for index, node in enumerate(workflow["nodes"]):
        if not isinstance(node, dict):
            raise ValueError(f"node {index} is not an object")
        node_type = node.get("type")
        if not isinstance(node_type, str) or not node_type.strip():
            raise ValueError(f"node {index} missing a valid 'type'")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate n8n workflow JSON files.")
    parser.add_argument("files", nargs="*", help="Workflow files to validate")
    args = parser.parse_args()

    files = [Path(path) for path in args.files]
    if not files:
        print("No workflow files supplied; skipping validation.")
        return 0

    failures: list[str] = []
    for path in files:
        try:
            validate_workflow(path)
            print(f"OK  {path}")
        except (ValueError, TypeError) as exc:
            failures.append(f"{path}: {exc}")

    if failures:
        print("\nValidation failed:", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1

    print(f"Validated {len(files)} workflow file(s) successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
