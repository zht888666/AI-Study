#!/usr/bin/env python3
"""Render overview.html from audit.json and overview.md."""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
from typing import Any


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig") as file:
        return file.read()


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def markdown_to_html(markdown: str) -> str:
    lines = markdown.splitlines()
    html_lines: list[str] = []
    in_list = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            html_lines.append("</ul>")
            in_list = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_list()
            continue
        if stripped.startswith("### "):
            close_list()
            html_lines.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        elif stripped.startswith("## "):
            close_list()
            html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("# "):
            close_list()
            html_lines.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(stripped[2:])}</li>")
        else:
            close_list()
            html_lines.append(f"<p>{html.escape(stripped)}</p>")

    close_list()
    return "\n".join(html_lines)


def default_template_path() -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", "assets", "overview-template.html"))


def project_title(audit: Any) -> str:
    if isinstance(audit, dict):
        project = audit.get("project")
        if isinstance(project, dict):
            return str(project.get("name") or project.get("title") or "Project Overview")
        if isinstance(project, str) and project:
            return project
    return "Project Overview"


def main() -> int:
    parser = argparse.ArgumentParser(description="Render overview.html.")
    parser.add_argument("--audit", required=True, help="Path to audit.json.")
    parser.add_argument("--overview", required=True, help="Path to overview.md.")
    parser.add_argument("--output", required=True, help="Output HTML path.")
    parser.add_argument("--template", default=default_template_path(), help="HTML template path.")
    args = parser.parse_args()

    try:
        audit = load_json(args.audit)
        overview_markdown = read_text(args.overview)
        template = read_text(args.template)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"render failed: {exc}", file=sys.stderr)
        return 1

    audit_json = json.dumps(audit, ensure_ascii=False, indent=2)
    rendered = template.replace("{{TITLE}}", html.escape(project_title(audit)))
    rendered = rendered.replace("{{OVERVIEW_HTML}}", markdown_to_html(overview_markdown))
    rendered = rendered.replace("{{AUDIT_JSON}}", html.escape(audit_json))

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(rendered)

    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
