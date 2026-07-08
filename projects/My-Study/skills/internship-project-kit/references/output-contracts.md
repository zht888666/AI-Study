# Output Contracts

Default output directory:

```text
project-prep/
  project-candidates.json
  project-candidates.md
  audit.json
  overview.md
  overview.html
  baseline-run-plan.md
  modification-plan.md
  resume-star.md
  core-code-walkthrough.md
  interview-qa.md
  ppt-prompts.md
  submission-checklist.md
```

## project-candidates.json

Top-level required fields:

- `queries`
- `sources`
- `generated_at`
- `candidates`
- `source_errors`

Candidate required fields:

- `source`
- `name`
- `url`
- `description`
- `language`
- `stars`
- `updated_at`

## audit.json

Top-level required fields:

- `project`
- `tech_stack`
- `entrypoints`
- `dependencies`
- `run_commands`
- `api_or_pages`
- `data_flow`
- `task_flow`
- `storage`
- `external_services`
- `risks`
- `talking_points`
- `recommended_modifications`

## overview.md

Include:

- Project purpose.
- Directory structure.
- Entrypoints.
- Dependency map.
- API/page/data/task flow.
- Baseline run path.
- Risks and blockers.
- Interview talking points.

## Interview Pack

All interview material must mark statements as:

- Completed.
- Planned modification.
- Optional extension.
