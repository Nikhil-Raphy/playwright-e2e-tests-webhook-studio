# ADR-0002: Run against the app's own compose file

## Status

Accepted

## Context

The tests must drive the app as it ships, on the same database and Redis, in two replay modes, and in three browsers.
Screenshots only match when fonts and rendering are the same on every machine. Chromium cannot be downloaded on
every network.

## Decision

- `compose.yaml` here includes the app repo's own `compose.yaml` (found through `APP_DIR`) with a small override,
  `docker/app.override.yaml`, so the tests run against the stack the app ships.
- The override reaches the app as `http://studio:17300`, sets the app's allowed origin to match, and publishes no
  port on the host. The name is not `app`: browsers force HTTPS for it, because the whole `.app` top-level domain is
  on the HSTS preload list.
- A second service, `app-local`, runs the same image in `local` replay mode, and `echo` gives replays a target.
  `app-local` reuses the app's image and `echo` runs from the runner image, so neither adds an image to pull.
- The runner is Playwright's own image, pinned by digest, which holds Chromium, Firefox and WebKit and their system
  libraries. It adds uv, Python 3.14 and this project. The `playwright` package is pinned to the image's version.
- Chromium runs as the full browser in its new headless mode, with the apps' plain-HTTP origins marked secure, so the
  page may use the clipboard. Chromium's headless shell ignores that flag.
- In CI, both repos check out the other at `main`.

## Consequences

- One command runs the whole suite, the same way on a laptop and in CI.
- A change to the app's compose file reaches the tests at once; a change that breaks them shows on the next run.
- Dependabot leaves the `playwright` package alone; it moves only with the image.
