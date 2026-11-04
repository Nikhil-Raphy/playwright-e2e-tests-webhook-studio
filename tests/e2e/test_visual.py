"""Browser tests that compare screenshots with approved ones, per browser, with ids, URLs and times masked."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

from webhook_studio_e2e.pages import SCREENSHOT_MASKS

if TYPE_CHECKING:
    from pytest_playwright_visual_snapshot.plugin import AssertSnapshot

    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage, HomePage

MASKS = list(SCREENSHOT_MASKS)


def test_given_home_with_a_bin_when_shown_then_it_matches_the_approved_screenshot(
    home: HomePage, assert_snapshot: AssertSnapshot
) -> None:
    """Given the home page listing one bin, when shown, then it matches the approved screenshot."""
    # Given
    home.goto().make_bin("visual")
    home.goto()
    expect(home.row("visual")).to_have_count(1)
    # When
    home.move_mouse_away()
    # Then
    assert_snapshot(home.page, mask_elements=MASKS)


def test_given_empty_bin_when_shown_then_it_matches_the_approved_screenshot(
    bin_page: BinPage, assert_snapshot: AssertSnapshot
) -> None:
    """Given a bin with no requests, when its page shows, then it matches the approved screenshot."""
    # Given
    expect(bin_page.empty_state).to_be_visible()
    # When
    bin_page.move_mouse_away()
    # Then
    assert_snapshot(bin_page.page, mask_elements=MASKS)


def test_given_json_request_when_body_tab_shows_then_it_matches_the_approved_screenshot(
    bin_page: BinPage, api: StudioApi, assert_snapshot: AssertSnapshot
) -> None:
    """Given a GET and a JSON POST, when the POST's Body tab shows, then the page matches the approved screenshot."""
    # Given
    api.send(bin_page.bin_id, method="GET", path="/status")
    api.send(bin_page.bin_id, path="/github", body=b'{"event": "push", "ids": [1, 2]}')
    expect(bin_page.rows).to_have_count(2)
    bin_page.row("/github").click()
    # When
    bin_page.open_tab("Body")
    expect(bin_page.body).to_contain_text('"event": "push"')
    bin_page.move_mouse_away()
    # Then
    assert_snapshot(bin_page.page, mask_elements=MASKS)


def test_given_reply_dialog_with_a_header_when_shown_then_it_matches_the_approved_screenshot(
    bin_page: BinPage, assert_snapshot: AssertSnapshot
) -> None:
    """Given the reply dialog with status 418, a header and a body, when shown, then it matches the approved one."""
    # Given
    dialog = bin_page.open_reply_settings()
    dialog.set_status(418)
    dialog.add_header("X-Tea", "yes")
    dialog.set_body("short and stout")
    # When
    bin_page.move_mouse_away()
    # Then
    assert_snapshot(dialog.dialog)
