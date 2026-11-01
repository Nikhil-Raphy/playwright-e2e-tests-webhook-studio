"""Fixtures for the browser tests: where the apps are, a REST client for each, the window size, and fresh bins."""

# Fixtures take other fixtures as arguments of the same name.
# pylint: disable=redefined-outer-name

from typing import TYPE_CHECKING, Any

import pytest

from webhook_studio_e2e.api import StudioApi
from webhook_studio_e2e.pages import BinPage, HomePage
from webhook_studio_e2e.settings import Settings

if TYPE_CHECKING:
    from collections.abc import Iterator

    from playwright.sync_api import Page

DESKTOP = {"width": 1440, "height": 900}


@pytest.fixture(scope="session")
def settings() -> Settings:
    """Read where the apps under test live.

    Returns:
        The settings.
    """
    return Settings.from_env()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args: dict[str, Any]) -> dict[str, Any]:
    """Open every browser context at desktop size, ready to take downloads.

    Args:
        browser_context_args: pytest-playwright's defaults.

    Returns:
        The context options.
    """
    return {**browser_context_args, "viewport": DESKTOP, "accept_downloads": True}


@pytest.fixture(scope="session")
def browser_type_launch_args(
    browser_type_launch_args: dict[str, Any], browser_name: str, settings: Settings
) -> dict[str, Any]:
    """Let Chromium treat the apps' plain-HTTP origins as secure, so the clipboard API exists there.

    Browsers offer `navigator.clipboard` only to HTTPS pages and localhost; in the test stack the apps are
    plain HTTP on service names. Only full Chromium honours the flag, not its headless shell, so Chromium runs
    use the full browser in its new headless mode, as real Chrome does, unless a channel such as msedge is given.

    Args:
        browser_type_launch_args: pytest-playwright's defaults.
        browser_name: The browser under test.
        settings: Where the apps are.

    Returns:
        The launch options.
    """
    if browser_name != "chromium":
        return browser_type_launch_args
    origins = ",".join(url for url in (settings.base_url, settings.local_replay_url) if url)
    args = [*browser_type_launch_args.get("args", []), f"--unsafely-treat-insecure-origin-as-secure={origins}"]
    return {"channel": "chromium", **browser_type_launch_args, "args": args}


@pytest.fixture(scope="session")
def api(settings: Settings) -> Iterator[StudioApi]:
    """Call the app in its default `restricted` replay mode.

    Args:
        settings: Where the app is.

    Yields:
        The client.
    """
    with StudioApi(settings.base_url) as client:
        yield client


@pytest.fixture(scope="session")
def local_api(settings: Settings) -> Iterator[StudioApi]:
    """Call the app in `local` replay mode; tests that need it skip when it is not set.

    Args:
        settings: Where the app is.

    Yields:
        The client.
    """
    if settings.local_replay_url is None or settings.echo_url is None:
        pytest.skip("E2E_LOCAL_REPLAY_URL and E2E_ECHO_URL are not both set")
    with StudioApi(settings.local_replay_url) as client:
        yield client


@pytest.fixture
def home(page: Page, settings: Settings) -> HomePage:
    """Give the home page's page object, not yet opened.

    Args:
        page: The browser page.
        settings: Where the app is.

    Returns:
        The page object.
    """
    return HomePage(page, settings.base_url)


@pytest.fixture
def bin_page(page: Page, settings: Settings, api: StudioApi) -> BinPage:
    """Make a bin through the API and open its page, live.

    Args:
        page: The browser page.
        settings: Where the app is.
        api: The REST client.

    Returns:
        The bin's page object.
    """
    return BinPage(page, settings.base_url).goto(api.create_bin("e2e"))
