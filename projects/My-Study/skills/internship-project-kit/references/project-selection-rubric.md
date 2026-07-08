# Project Selection Rubric

Score candidate projects with a 100-point rubric.

| Dimension | Weight | What To Check |
| --- | ---: | --- |
| JD match | 30 | Stack, role responsibilities, domain, API/page/data/infra relevance. |
| Speed to start | 25 | Clear README, simple dependencies, recent maintenance, small enough scope. |
| Interview talking points | 20 | Architecture, tradeoffs, data flow, performance, reliability, testing, AI experiment design. |
| Run cost | 15 | Local feasibility, Docker support, database complexity, GPU/cloud requirements. |
| Modification space | 10 | Obvious but bounded improvements that match the JD. |

Reject or downgrade projects when:

- The license is missing or incompatible for public reuse.
- The project is archived, abandoned, or too large for the user's time budget.
- The project cannot be explained by the candidate's current level.
- Running it requires paid resources the user does not have.
- It is a framework/library itself rather than an application project, unless the JD asks for framework or system work.

Recommendation output for each project:

- Match summary.
- Why it is fast or slow to start.
- 2-4 interview talking points.
- Expected run cost.
- 1-3 feasible modifications.
- Risks and mitigation.
- Source URL and verified metadata.
