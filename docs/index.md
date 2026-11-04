# Webhook Studio browser tests

Playwright end-to-end tests for [Reflex FastAPI Webhook Studio](https://github.com/Nikhil-Raphy/reflex-fastapi-webhook-studio),
written in Python with pytest. They drive the real app in Chromium, Firefox and WebKit, and check:

- **What users do:** make and open bins, watch requests arrive live, filter, search, delete, export, set a bin's
  reply, and replay requests in both replay modes.
- **Accessibility:** every page, tab and dialog is scanned with axe-core for WCAG 2.2 AA. Any finding fails the test.
- **Looks:** screenshots are compared with approved ones, one set per browser, with the version, ids, URLs and times
  masked.

The [latest report](report/) shows the last run on `main`, with history.

## Where to start

- [Run the tests](guide/running.md), on your machine or in Docker.
- [Write a test](guide/writing.md): page objects, Given / When / Then, and locators.
- [Read the reports](guide/reports.md): JUnit, pytest-html, Allure, and traces.
- [Decisions](adr/index.md): why the suite is built the way it is.
