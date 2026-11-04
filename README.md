# Playwright end-to-end tests for Webhook Studio

[![CI](https://github.com/Nikhil-Raphy/playwright-e2e-tests-webhook-studio/actions/workflows/ci.yml/badge.svg)](https://github.com/Nikhil-Raphy/playwright-e2e-tests-webhook-studio/actions/workflows/ci.yml)
[![Allure report](https://img.shields.io/badge/report-Allure-orange)](https://nikhil-raphy.github.io/playwright-e2e-tests-webhook-studio/report/)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue)](.python-version)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-green)](LICENSE)

Browser tests for [Reflex FastAPI Webhook Studio](https://github.com/Nikhil-Raphy/reflex-fastapi-webhook-studio), a
web app that catches, inspects and replays webhooks. The tests use [Playwright](https://playwright.dev/python/) for
Python with pytest, and drive the real app in **Chromium, Firefox and WebKit**.

## What the suite checks

| Area           | Examples                                                                                          |
| -------------- | ------------------------------------------------------------------------------------------------- |
| Bins           | Make a bin, open one by id or URL, see the bins this browser made, and when they expire.          |
| Requests       | Overview fields; JSON, form, text and binary bodies; query strings; masked secret headers.         |
| Live updates   | A request shows within a second, in every open tab; renames show at once.                         |
| Finding        | Method filter, search, Clear filters, and older requests by scrolling or by "Load older".         |
| Deleting       | One request, every request or the bin, in every tab, and "Don't ask again".                       |
| Replies        | Status, headers, body and delay of a bin's reply; bad headers are refused.                        |
| Replay         | Refused to private addresses in `restricted` mode; reaches an echo service in `local` mode.       |
| Clipboard      | Copy URL and Copy as curl (Chromium).                                                            |
| Accessibility  | Every page, tab and dialog scanned with axe-core for WCAG 2.2 AA; any finding fails.              |
| Looks          | Screenshots compared with approved ones, per browser, with ids, URLs and times masked.            |

## Playwright features in use

- **Locators by role and label** (`get_by_role`, `get_by_label`, `get_by_placeholder`), then `data-testid`; no CSS
  classes or XPath.
- **Web-first assertions** (`expect(...)`) that wait by themselves, so there are no sleeps.
- **Page objects** for each page and dialog, so tests read as user steps.
- **Several tabs in one browser context**, to check live updates across tabs.
- **Downloads** (`expect_download`) for exports and binary bodies, checked byte for byte.
- **Clipboard** reads, with permissions granted per context.
- **Browser launch options** per browser, and **context options** for size and downloads.
- **Traces, videos and screenshots** kept for every failed test.
- **Screenshot comparison** with masks, and **axe-core** injected into the page.
- **Test data through the REST API** with httpx, so the browser does only what each scenario tests.

## Quick start

You need Docker with Compose, and the app repo cloned beside this one.

```bash
git clone https://github.com/Nikhil-Raphy/reflex-fastapi-webhook-studio.git
git clone https://github.com/Nikhil-Raphy/playwright-e2e-tests-webhook-studio.git
cd playwright-e2e-tests-webhook-studio
export POSTGRES_PASSWORD=pick-any-local-password E2E_UID=$(id -u) E2E_GID=$(id -g)
docker compose build
docker compose run --rm tests                                   # unit and browser tests, in Chromium
docker compose run --rm tests pytest tests/e2e --browser webkit
docker compose down --volumes
```

`docker compose run` starts the app from its own compose file, with PostgreSQL and Redis, a second copy in `local`
replay mode, and an echo service, and waits until each is healthy. The [running guide](docs/guide/running.md) covers
running against an app on your machine, and every option.

## How it is built

```text
src/webhook_studio_e2e/     typed support package
├── pages/                  page objects: AppPage, HomePage, BinPage, ConfirmDialog, ReplyDialog
├── api.py                  REST client for test data
├── accessibility.py        axe-core scan and readable findings
├── echo.py                 echo server, the target for replays
├── settings.py             where the apps are, from E2E_* variables
└── _version.py             the version: the one place to change it
tests/
├── unit/                   tests for the support package, no browser
└── e2e/                    browser tests, one file per area
snapshots/                  approved screenshots, per browser
docker/                     runner image, and the override for the app's compose file
```

- Python 3.14, uv, Ruff, pylint and `mypy --strict`, with a line length of 120.
- Every test states its scenario in Given / When / Then form.
- Coverage of the support package is at least 90%, from the unit tests and the browser run together.
- CI runs lint, unit tests, the browser tests in all three browsers, and an audit of packages and workflows. On
  `main`, it publishes the docs and an Allure report with history.

The [decision records](docs/adr/index.md) explain the main choices.

## Reports

Each CI run keeps JUnit XML, a pytest-html page and Allure results per browser, plus traces, videos and screenshot
diffs for failed tests. The [reports guide](docs/guide/reports.md) shows how to read them.

## Links

- [Docs site](https://nikhil-raphy.github.io/playwright-e2e-tests-webhook-studio/)
- [Latest Allure report](https://nikhil-raphy.github.io/playwright-e2e-tests-webhook-studio/report/)
- [Webhook Studio](https://github.com/Nikhil-Raphy/reflex-fastapi-webhook-studio)

## Contributions

This is a personal project. It takes no code contributions for now, but you may open an issue to report a bug or
suggest a scenario.

## License

[Apache-2.0](LICENSE). Copyright 2026 Nikhil-Raphy.
