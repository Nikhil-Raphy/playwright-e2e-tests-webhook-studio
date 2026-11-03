## What this changes

<!-- Say what the change does and why. -->

## Checks

- [ ] `uv run ruff check .`, `uv run ruff format --check .`, `uv run pylint src tests` and `uv run mypy src tests`
      pass.
- [ ] `docker compose run --rm tests pytest --browser chromium --cov` passes with at least 90% coverage.
- [ ] The browser tests pass in Firefox and WebKit too.
- [ ] Each new test follows Given / When / Then, and reaches the page only through a page object.
- [ ] New or changed screenshots were made in the runner image and reviewed by eye.
