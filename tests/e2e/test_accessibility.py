"""Browser tests that scan each page, tab and dialog with axe-core for WCAG 2.2 AA, and fail on any finding."""

from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import expect

from webhook_studio_e2e.accessibility import describe, scan
from webhook_studio_e2e.pages import BinPage

if TYPE_CHECKING:
    from collections.abc import Callable

    from playwright.sync_api import Page

    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import ConfirmDialog, HomePage
    from webhook_studio_e2e.settings import Settings

UNKNOWN_BIN = "AbCdEfGhIjKlMnOpQrStUv"
JSON = {"content-type": "application/json", "authorization": "Bearer hidden"}


def assert_accessible(page: Page) -> None:
    """Fail with every finding when what the page shows now breaks a WCAG 2.2 AA rule.

    Args:
        page: The browser page.
    """
    found = scan(page)
    assert not found, describe(found)


def test_given_home_with_a_bin_when_scanned_then_it_meets_wcag_22_aa(home: HomePage) -> None:
    """Given the home page listing a bin, when scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    home.goto().make_bin("listed")
    home.goto()
    expect(home.row("listed")).to_have_count(1)
    # When / Then
    assert_accessible(home.page)


def test_given_empty_bin_when_scanned_then_it_meets_wcag_22_aa(bin_page: BinPage) -> None:
    """Given a bin with no requests, when its page is scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    expect(bin_page.empty_state).to_be_visible()
    # When / Then
    assert_accessible(bin_page.page)


@pytest.mark.parametrize("tab", ["Overview", "Headers", "Query", "Body", "Replay"])
def test_given_json_request_when_each_tab_is_scanned_then_it_meets_wcag_22_aa(
    bin_page: BinPage, api: StudioApi, tab: str
) -> None:
    """Given a JSON request with a query and a secret header, when each tab is scanned, then none breaks a rule."""
    # Given
    api.send(bin_page.bin_id, method="POST", path="/github?x=1", body=b'{"a": [1, true, null]}', headers=JSON)
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab(tab)
    expect(bin_page.tab_panel).to_be_visible()
    # Then
    assert_accessible(bin_page.page)


@pytest.mark.parametrize(
    ("content_type", "body"),
    [
        ("application/x-www-form-urlencoded", b"a=1&b=2"),
        ("application/octet-stream", b"\x00\xff"),
        ("text/plain", b"hi"),
    ],
    ids=["form", "binary", "text"],
)
def test_given_other_bodies_when_body_tab_is_scanned_then_it_meets_wcag_22_aa(
    bin_page: BinPage, api: StudioApi, content_type: str, body: bytes
) -> None:
    """Given a form, binary or text body, when the Body tab is scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    api.send(bin_page.bin_id, path="/body", body=body, headers={"content-type": content_type})
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Body")
    expect(bin_page.body).to_be_visible()
    # Then
    assert_accessible(bin_page.page)


def test_given_reply_dialog_with_a_header_and_body_when_scanned_then_it_meets_wcag_22_aa(bin_page: BinPage) -> None:
    """Given the reply dialog with a header row and a custom body, when scanned, then it breaks no rule."""
    # Given
    dialog = bin_page.open_reply_settings()
    dialog.add_header("X-Tea", "yes")
    dialog.set_body("short and stout")
    # When / Then
    assert_accessible(bin_page.page)


def test_given_reply_error_when_scanned_then_it_meets_wcag_22_aa(bin_page: BinPage) -> None:
    """Given the reply dialog showing an error, when scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    dialog = bin_page.open_reply_settings()
    dialog.add_header("Set-Cookie", "a=b")
    dialog.save()
    expect(dialog.error).to_be_visible()
    # When / Then
    assert_accessible(bin_page.page)


@pytest.mark.parametrize(
    "ask",
    [BinPage.ask_delete_request, BinPage.ask_clear, BinPage.ask_delete_bin],
    ids=["Delete request", "Clear", "Delete bin"],
)
def test_given_each_delete_dialog_when_scanned_then_it_meets_wcag_22_aa(
    bin_page: BinPage, api: StudioApi, ask: Callable[[BinPage], ConfirmDialog]
) -> None:
    """Given each delete confirmation, when scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    api.send(bin_page.bin_id, body=b"x")
    expect(bin_page.rows).to_have_count(1)
    # When
    dialog = ask(bin_page)
    expect(dialog.dialog).to_be_visible()
    # Then
    assert_accessible(bin_page.page)


def test_given_refused_replay_when_scanned_then_it_meets_wcag_22_aa(bin_page: BinPage, api: StudioApi) -> None:
    """Given the Replay tab showing a refused target, when scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    api.send(bin_page.bin_id, body=b"x")
    expect(bin_page.rows).to_have_count(1)
    bin_page.replay("http://127.0.0.1:9/")
    expect(bin_page.replay_error).to_be_visible()
    # When / Then
    assert_accessible(bin_page.page)


def test_given_unknown_bin_when_scanned_then_it_meets_wcag_22_aa(page: Page, settings: Settings) -> None:
    """Given the page for a bin id that does not exist, when scanned, then it breaks no WCAG 2.2 AA rule."""
    # Given
    unknown = BinPage(page, settings.base_url).open(UNKNOWN_BIN)
    expect(unknown.text("No bin has this id.")).to_be_visible()
    # When / Then
    assert_accessible(page)
