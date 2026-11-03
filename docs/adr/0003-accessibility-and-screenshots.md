# ADR-0003: Accessibility and screenshot checks

## Status

Accepted

## Context

The suite should catch more than broken flows: pages that fail people who use a screen reader or need strong
contrast, and pages whose looks change by accident. Playwright's own screenshot compare, `toHaveScreenshot`, exists
only in its TypeScript runner.

## Decision

- **Accessibility:** axe-core, through axe-playwright-python, scans every page, tab and dialog in each browser, for the
  WCAG 2.0, 2.1 and 2.2 rules at levels A and AA. Any finding fails the test. The scan waits until no animation
  runs, since colours measured mid-fade fail the contrast rule. Open dropdown menus are not scanned: while one is
  open, Radix hides the rest of the page from screen readers but leaves it focusable, which axe flags.
- **Screenshots:** pytest-playwright-visual-snapshot compares each screenshot with an approved one, kept in
  `snapshots/`, one per browser. Ids, URLs, relative times and the curl command, which change on every run, are
  masked. Approved screenshots are made only in the runner image.

## Consequences

- The first scans found real problems, which the app fixed: unnamed controls, and contrast below 4.5:1 on the default
  blue accent, on soft buttons and badges, and in the code theme.
- A deliberate change to how a page looks needs new approved screenshots, made with `--update-snapshots` and reviewed
  by eye.
