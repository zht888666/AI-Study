---
name: internship-project-kit
description: Use when Codex needs to turn a target JD or internship job description into a computer science project preparation package for low-experience candidates, including intake questions, GitHub/Gitee project discovery, cloned-project audit, baseline run planning, interview-focused modifications, resume STAR bullets, code walkthroughs, interview Q&A, PPT prompts, and submission checklists.
---

# JD 实习项目准备工具包

## Overview

把目标 JD 转成一个能投递、能面试、能讲清的计算机实习项目准备闭环。优先帮助 0 经验或低经验候选人用最短路径完成选题、理解、运行、改造、简历表达和面试材料准备。

支持后端、前端、全栈、移动端、测试开发、数据工程、云原生/DevOps、安全、系统、AI/算法等方向。保持诚实表达，区分已经完成、计划改造和可选扩展。

## Workflow

1. Parse the JD: extract responsibilities, requirements, stack, business domain, location, degree, graduation window, and implicit screening signals.
2. Intake the candidate context: if the user only provides a JD, ask the short intake from `references/intake-and-depth.md`.
3. Discover projects: generate 3-6 search queries from the JD and, when network access is available, run `scripts/fetch_project_candidates.py`.
4. Rank candidates: use `references/project-selection-rubric.md` to recommend 2-3 projects by match, speed, talking points, run cost, and modification space.
5. Audit cloned code when a local path is provided: inspect structure, entrypoints, dependencies, API/pages/data flow/task flow, storage, services, risks, and talking points.
6. Plan baseline run: follow `references/baseline-run-playbook.md`; prefer the smallest local runnable path before remote resources.
7. Plan interview-worthy modifications: choose 1-3 high-value changes tied to the JD.
8. Generate the interview pack: follow `references/interview-pack-playbook.md` and `references/output-contracts.md`.

## Running Depth

- `interview-only`: do not run code; prepare understanding, project selection, resume, and interview material.
- `smoke-test`: verify the smallest startup command or core script.
- `local-full-run`: run the main local workflow end to end.
- `remote-full-run`: plan cloud server, database, object storage, GPU/AutoDL, or other remote resources only when local execution is insufficient.

## Project Discovery

Use API-first discovery. Do not invent repository stars, last update time, license, activity, or source URLs.

When the user asks for project recommendations and no local project path is provided:

1. Read `references/crawler-playbook.md`.
2. Build search queries from the JD stack, business direction, and role.
3. Run the crawler when network access is available:

```powershell
E:\anaconda3\python.exe internship-project-kit\scripts\fetch_project_candidates.py --query "fastapi internship project" --language Python --sources github,gitee --per-source 10 --output project-candidates.json
```

4. If one source fails, continue with the other source and mention `source_errors`.
5. If all network discovery fails, ask the user for project links or a cloned path.

The crawler only fetches public metadata. It must not clone, run, or modify remote code.

## Local Project Audit

When a cloned project path is available, prioritize local inspection over generic advice.

Produce:

- `audit.json`
- `overview.md`
- `overview.html`
- `baseline-run-plan.md`
- `modification-plan.md`

Use `scripts/validate_audit_json.py` before treating `audit.json` as complete. Use `scripts/render_overview_html.py` to generate the HTML overview from `audit.json` and `overview.md`.

## Interview Pack

Generate material that a candidate can defend honestly:

- STAR resume project
- Core code walkthrough
- Interviewer challenge Q&A
- PPT prompts
- Submission checklist

Always label statements as one of: completed, planned modification, optional extension. Do not package unimplemented plans as completed experience.

## Resources

- `references/intake-and-depth.md`: intake questions and run depth.
- `references/project-selection-rubric.md`: scoring model for candidate projects.
- `references/crawler-playbook.md`: query generation and API crawler rules.
- `references/output-contracts.md`: required output files and JSON fields.
- `references/role-playbooks.md`: role-specific project and modification guidance.
- `references/baseline-run-playbook.md`: baseline run planning rules.
- `references/interview-pack-playbook.md`: resume, code explanation, Q&A, PPT, and checklist guidance.
- `scripts/fetch_project_candidates.py`: fetch and normalize public GitHub/Gitee repository metadata.
- `scripts/validate_candidates_json.py`: validate crawler output.
- `scripts/validate_audit_json.py`: validate local project audit output.
- `scripts/render_overview_html.py`: render `overview.html`.
