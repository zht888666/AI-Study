# Crawler Playbook

Use API-first discovery for public project metadata. Do not scrape pages to bypass platform limits.

## Query Generation

Extract 3-6 query combinations from the JD:

- Role keyword: backend, frontend, fullstack, mobile, testing, data engineering, devops, security, system, AI.
- Stack keyword: Java, Spring Boot, Python, FastAPI, Vue, React, Go, Docker, Kubernetes, Redis, MySQL, RAG, LangChain.
- Business keyword: ecommerce, CRM, recommendation, monitoring, chat, document QA, ticketing, payment, log analysis.
- Project form: project, demo, starter, system, platform, dashboard, API.

Examples:

- Backend: `fastapi mysql redis project`, `spring boot order system`, `go gin api dashboard`.
- Frontend: `react dashboard project`, `vue admin system`, `nextjs ecommerce`.
- AI: `rag fastapi langchain project`, `document qa vector database`, `llm agent tools`.
- DevOps: `kubernetes monitoring dashboard`, `docker ci cd project`, `prometheus grafana demo`.
- Security: `vulnerability scanner project`, `web security lab`, `jwt auth api`.

## Script Use

Run:

```powershell
E:\anaconda3\python.exe scripts\fetch_project_candidates.py --query "fastapi mysql redis project" --language Python --sources github,gitee --per-source 10 --output project-candidates.json
```

Use `GITHUB_TOKEN` and `GITEE_TOKEN` only from environment variables. Never print or write tokens.

## Field Meaning

- `stars`: popularity signal, not a quality guarantee.
- `updated_at` and `pushed_at`: activity signals.
- `license`: reuse and attribution signal; missing license is a risk.
- `topics`: useful for matching JD keywords.
- `clone_url`: only a link for later user-approved cloning.

## Failure Handling

- If GitHub succeeds and Gitee returns `[]`, continue with GitHub and mention Gitee empty results.
- If one source fails, keep candidates from the other source and include `source_errors`.
- If all sources fail, ask for user-provided project links or a cloned local path.
- Never invent stars, license, update time, or activity.
