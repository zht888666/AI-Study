#!/usr/bin/env python3
"""Validate audit.json for the internship project kit."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


REQUIRED_FIELDS = {
    "project",
    "tech_stack",
    "entrypoints",
    "dependencies",
    "run_commands",
    "api_or_pages",
    "data_flow",
    "task_flow",
    "storage",
    "external_services",
    "risks",
    "talking_points",
    "recommended_modifications",
}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate audit.json.")
    parser.add_argument("path", help="Path to audit.json.")
    args = parser.parse_args()

    try:
        data = load_json(args.path)
    except OSError as exc:
        print(f"cannot read file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("top-level value must be an object", file=sys.stderr)
        return 1

    missing = sorted(REQUIRED_FIELDS - set(data))
    if missing:
        print(f"missing audit fields: {', '.join(missing)}", file=sys.stderr)
        return 1

    print(f"valid audit JSON: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
