# Run the tests

## In Docker (the same as CI)

You need Docker with Compose, and the app repo checked out beside this one:

```text
My Repos/
├── reflex-fastapi-webhook-studio/
└── playwright-e2e-tests-webhook-studio/
```

From this repo's folder:

```bash
export POSTGRES_PASSWORD=pick-any-local-password E2E_UID=$(id -u) E2E_GID=$(id -g)
docker compose build
docker compose run --rm tests                                   # unit and browser tests, in Chromium
docker compose run --rm tests pytest tests/e2e --browser firefox
docker compose run --rm tests pytest tests/e2e --browser webkit
docker compose down --volumes                                   # stop the stack and drop its data
```

`docker compose run` starts the whole stack first and waits until each part is healthy:

| Service     | What it is                                                                                     |
| ----------- | ---------------------------------------------------------------------------------------------- |
| `app`       | Webhook Studio, built from the app repo's own `compose.yaml`, in `restricted` replay mode.       |
| `app-local` | The same image in `local` replay mode, so replays may reach the echo service.                  |
| `migrate`   | Runs the app's database migrations once.                                                       |
| `postgres`  | PostgreSQL, from the app's compose file.                                                       |
| `redis`     | Redis, from the app's compose file.                                                            |
| `echo`      | `python -m webhook_studio_e2e.echo`: replies to any request with what it received.             |
| `tests`     | The runner: Playwright's image with Chromium, Firefox and WebKit, Python 3.14 and this project. |

The app repo can live elsewhere: set `APP_DIR` to its path.

`E2E_UID` and `E2E_GID` make the runner write reports and screenshots as you, not as root.

## On your machine

Start the app in production mode, then point the tests at it:

```bash
uv sync
E2E_BASE_URL=http://localhost:17300 uv run pytest tests/e2e --browser-channel msedge
```

Use any installed browser channel (`chrome`, `msedge`), or run `uv run playwright install` first. The replay tests
that need `local` mode skip unless you also set `E2E_LOCAL_REPLAY_URL` and `E2E_ECHO_URL`, and the screenshot tests
only match inside the runner image, since fonts differ between machines. Pass `--disable-visual-snapshots` to skip
them.

## Settings

| Variable               | Meaning                                                     | Default                  |
| ---------------------- | ----------------------------------------------------------- | ------------------------ |
| `E2E_BASE_URL`         | The app in `restricted` replay mode.                        | `http://localhost:17300` |
| `E2E_LOCAL_REPLAY_URL` | The app in `local` replay mode. Its tests skip without it.  | none                     |
| `E2E_ECHO_URL`         | The echo service, as the `local` app reaches it.            | none                     |

## Useful options

| Option                                    | What it does                                                         |
| ----------------------------------------- | -------------------------------------------------------------------- |
| `--browser chromium\|firefox\|webkit`     | The browser to use.                                                  |
| `--headed --slowmo 500`                   | Watch the browser work, half a second per step (outside Docker).     |
| `--update-snapshots`                      | Write new approved screenshots; review them before you commit.       |
| `--reruns 1`                              | Retry a failed test once, so a flaky test shows as flaky.            |
| `--cov`                                   | Measure coverage of the support package; 90% is the bar.             |
