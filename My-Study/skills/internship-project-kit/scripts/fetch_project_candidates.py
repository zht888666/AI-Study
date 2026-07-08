#!/usr/bin/env python3
"""Fetch public repository metadata from GitHub and Gitee.

This script is intentionally API-first and metadata-only. It does not clone,
download archives, execute remote code, save tokens, or print tokens.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


DEFAULT_MIN_STARS = {
    "github": 50,
    "gitee": 10,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_url(base_url: str, params: dict[str, Any]) -> str:
    clean_params = {key: value for key, value in params.items() if value not in (None, "")}
    return f"{base_url}?{urllib.parse.urlencode(clean_params)}"


def fetch_json(url: str, headers: dict[str, str], timeout: int = 25) -> Any:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            text = response.read().decode(charset, errors="replace")
            if not text.strip():
                return None
            return json.loads(text)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"network error: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON: {exc}") from exc


def normalize_license(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("spdx_id") or value.get("name") or value.get("key") or ""
    return str(value)


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def first_present(item: dict[str, Any], keys: list[str], default: Any = "") -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return default


def date_matches(value: str, updated_after: str | None) -> bool:
    if not updated_after:
        return True
    if not value:
        return False
    return value[:10] >= updated_after[:10]


def normalize_github(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": "github",
        "name": item.get("full_name") or item.get("name") or "",
        "url": item.get("html_url") or "",
        "description": item.get("description") or "",
        "language": item.get("language") or "",
        "stars": as_int(item.get("stargazers_count")),
        "forks": as_int(item.get("forks_count")),
        "open_issues": as_int(item.get("open_issues_count")),
        "updated_at": item.get("updated_at") or "",
        "pushed_at": item.get("pushed_at") or "",
        "license": normalize_license(item.get("license")),
        "topics": item.get("topics") or [],
        "clone_url": item.get("clone_url") or "",
        "raw": {
            "archived": item.get("archived"),
            "default_branch": item.get("default_branch"),
            "size": item.get("size"),
        },
    }


def normalize_gitee(item: dict[str, Any]) -> dict[str, Any]:
    full_name = first_present(item, ["full_name", "human_name", "path_with_namespace", "name"])
    url = first_present(item, ["html_url", "url"])
    if full_name and not str(url).startswith("http"):
        url = f"https://gitee.com/{full_name}"
    return {
        "source": "gitee",
        "name": full_name or "",
        "url": url or "",
        "description": item.get("description") or "",
        "language": item.get("language") or "",
        "stars": as_int(first_present(item, ["stargazers_count", "stars_count", "stars"], 0)),
        "forks": as_int(first_present(item, ["forks_count", "forks"], 0)),
        "open_issues": as_int(first_present(item, ["open_issues_count", "issues_count"], 0)),
        "updated_at": first_present(item, ["updated_at", "last_push_at"], ""),
        "pushed_at": first_present(item, ["pushed_at", "last_push_at"], ""),
        "license": normalize_license(item.get("license")),
        "topics": item.get("topics") or item.get("tags") or [],
        "clone_url": first_present(item, ["clone_url", "https_url", "ssh_url"], ""),
        "raw": {
            "default_branch": item.get("default_branch"),
            "namespace": item.get("namespace"),
            "project_creator": item.get("project_creator"),
        },
    }


def search_github(query: str, language: str | None, per_source: int, min_stars: int, updated_after: str | None) -> list[dict[str, Any]]:
    q_parts = [query]
    if language:
        q_parts.append(f"language:{language}")
    if min_stars > 0:
        q_parts.append(f"stars:>={min_stars}")
    if updated_after:
        q_parts.append(f"pushed:>={updated_after[:10]}")

    token = os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "internship-project-kit",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = build_url(
        "https://api.github.com/search/repositories",
        {
            "q": " ".join(q_parts),
            "sort": "stars",
            "order": "desc",
            "per_page": min(max(per_source, 1), 100),
            "page": 1,
        },
    )
    data = fetch_json(url, headers)
    items = data.get("items", []) if isinstance(data, dict) else []
    return [normalize_github(item) for item in items if isinstance(item, dict)]


def search_gitee(query: str, language: str | None, per_source: int, min_stars: int, updated_after: str | None) -> list[dict[str, Any]]:
    token = os.environ.get("GITEE_TOKEN")
    headers = {
        "Accept": "application/json",
        "User-Agent": "internship-project-kit",
    }
    params: dict[str, Any] = {
        "q": query,
        "sort": "stars_count",
        "order": "desc",
        "page": 1,
        "per_page": min(max(per_source, 1), 100),
    }
    if language:
        params["language"] = language
    if token:
        params["access_token"] = token

    url = build_url("https://gitee.com/api/v5/search/repositories", params)
    data = fetch_json(url, headers)
    if not isinstance(data, list):
        return []

    candidates = []
    for item in data:
        if not isinstance(item, dict):
            continue
        candidate = normalize_gitee(item)
        if candidate["stars"] < min_stars:
            continue
        if not date_matches(candidate["updated_at"] or candidate["pushed_at"], updated_after):
            continue
        candidates.append(candidate)
    return candidates


def dedupe(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for candidate in candidates:
        key = (candidate.get("source", ""), candidate.get("url", "") or candidate.get("name", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(candidate)
    return result


def parse_sources(value: str) -> list[str]:
    sources = [source.strip().lower() for source in value.split(",") if source.strip()]
    unknown = [source for source in sources if source not in {"github", "gitee"}]
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown source(s): {', '.join(unknown)}")
    return sources or ["github", "gitee"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch public GitHub/Gitee project candidates.")
    parser.add_argument("--query", action="append", required=True, help="Search query. Can be passed multiple times.")
    parser.add_argument("--language", help="Optional language filter, such as Python, Java, JavaScript, Go.")
    parser.add_argument("--sources", type=parse_sources, default=["github", "gitee"], help="Comma-separated sources: github,gitee.")
    parser.add_argument("--per-source", type=int, default=10, help="Number of results per source and query.")
    parser.add_argument("--min-stars", type=int, help="Minimum stars for all sources. Defaults: GitHub 50, Gitee 10.")
    parser.add_argument("--updated-after", help="Keep repositories updated on or after YYYY-MM-DD.")
    parser.add_argument("--output", default="project-candidates.json", help="Output JSON path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    candidates: list[dict[str, Any]] = []
    source_errors: list[dict[str, str]] = []

    for query in args.query:
        for source in args.sources:
            min_stars = args.min_stars if args.min_stars is not None else DEFAULT_MIN_STARS[source]
            try:
                if source == "github":
                    source_candidates = search_github(query, args.language, args.per_source, min_stars, args.updated_after)
                else:
                    source_candidates = search_gitee(query, args.language, args.per_source, min_stars, args.updated_after)
                if not source_candidates:
                    source_errors.append(
                        {
                            "source": source,
                            "query": query,
                            "kind": "empty_result",
                            "message": "source returned no candidates after filters",
                        }
                    )
                candidates.extend(source_candidates)
            except RuntimeError as exc:
                source_errors.append(
                    {
                        "source": source,
                        "query": query,
                        "kind": "fetch_error",
                        "message": str(exc),
                    }
                )

    candidates = dedupe(candidates)
    candidates.sort(key=lambda item: (as_int(item.get("stars")), item.get("updated_at") or ""), reverse=True)

    output = {
        "queries": args.query,
        "sources": args.sources,
        "generated_at": utc_now(),
        "candidates": candidates,
        "source_errors": source_errors,
    }

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"wrote {len(candidates)} candidates to {args.output}")
    if source_errors:
        print(f"recorded {len(source_errors)} source status entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
