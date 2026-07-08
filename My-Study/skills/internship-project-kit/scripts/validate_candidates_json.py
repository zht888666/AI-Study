#!/usr/bin/env python3
"""Validate project-candidates.json produced by fetch_project_candidates.py."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


TOP_LEVEL_REQUIRED = {"queries", "sources", "candidates", "source_errors"}
CANDIDATE_REQUIRED = {"source", "name", "url", "description", "language", "stars", "updated_at"}


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def validate(path: str) -> list[str]:
    errors: list[str] = []
    try:
        data = load_json(path)
    except OSError as exc:
        return [f"cannot read file: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"invalid JSON: {exc}"]

    if not isinstance(data, dict):
        return ["top-level value must be an object"]

    missing = sorted(TOP_LEVEL_REQUIRED - set(data))
    if missing:
        errors.append(f"missing top-level fields: {', '.join(missing)}")

    if "queries" in data and not isinstance(data["queries"], list):
        errors.append("queries must be a list")
    if "sources" in data and not isinstance(data["sources"], list):
        errors.append("sources must be a list")
    if "source_errors" in data and not isinstance(data["source_errors"], list):
        errors.append("source_errors must be a list")

    candidates = data.get("candidates")
    if candidates is None:
        return errors
    if not isinstance(candidates, list):
        errors.append("candidates must be a list")
        return errors

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            errors.append(f"candidates[{index}] must be an object")
            continue
        missing_candidate = sorted(CANDIDATE_REQUIRED - set(candidate))
        if missing_candidate:
            errors.append(f"candidates[{index}] missing fields: {', '.join(missing_candidate)}")
        for key in CANDIDATE_REQUIRED - {"stars"}:
            if key in candidate and candidate[key] is None:
                errors.append(f"candidates[{index}].{key} must not be null")
        if "stars" in candidate and not isinstance(candidate["stars"], int):
            errors.append(f"candidates[{index}].stars must be an integer")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate project-candidates.json.")
    parser.add_argument("path", help="Path to project-candidates.json.")
    args = parser.parse_args()

    errors = validate(args.path)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid candidates JSON: {args.path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
