# ADR-0001: Page objects and plain pytest

## Status

Accepted

## Context

The suite must be easy to read, easy to change when the app's pages change, and written in Python 3.14 with the same
rules as the app: Ruff, pylint, `mypy --strict`, Google docstrings and a line length of 120. Tests in the app repo
already name and mark their Given / When / Then parts.

## Decision

- Tests use pytest with pytest-playwright's sync API. Each test name and docstring states its scenario in Given /
  When / Then form, and `# Given`, `# When` and `# Then` comments mark the parts of its body. There are no `.feature`
  files.
- A typed package, `src/webhook_studio_e2e/`, holds everything a test uses: page objects, a REST client, the echo
  server, the accessibility helper and the settings. `tests/` holds the tests and their fixtures.
- Tests hold no locators. Page objects find elements by role and label first, then by the app's `data-testid`
  attributes, and never by CSS classes or XPath.
- Tests make their data through the app's REST API, and each makes its own bin, so tests run in any order.

## Consequences

- When a page changes, one page object changes, not every test.
- The package is typed and tested like any library: unit tests for the helpers, and the browser run for the page
  objects, with coverage of at least 90%.
- Where the app had no role, label or test id on an element, the app gained one (the bin label, the method filter's
  name and the error callouts).
