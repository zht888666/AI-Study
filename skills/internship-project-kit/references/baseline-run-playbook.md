# Baseline Run Playbook

Plan the smallest credible run first.

## Local First

1. Identify language/runtime from lockfiles and manifests.
2. Find README startup commands, Docker Compose, Makefile, package scripts, or entrypoint files.
3. Prefer a smoke path: health endpoint, sample CLI command, single notebook, one API call, or one UI route.
4. List exact commands, working directory, expected output, and likely blockers.
5. Only add database, object storage, queue, GPU, or cloud resources when the project requires them.

## Remote Resources

Use remote resources only for `remote-full-run` or when local resources are insufficient.

Plan:

- Cloud server specs.
- Database/service choice.
- Storage and secrets.
- Network ports.
- Cost and cleanup.
- What proves the run succeeded.

## Validation

Separate:

- Static audit only.
- Import/smoke-tested.
- Runtime verified.

Do not imply runtime verification unless commands were actually run.
