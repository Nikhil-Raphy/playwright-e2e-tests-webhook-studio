"""Browser tests for deleting: one request, every request, or the bin, and "Don't ask again"."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage, HomePage


def test_given_request_open_in_two_tabs_when_user_deletes_it_then_it_is_gone_from_both(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a request open in two tabs, when the user deletes it in one, then it is gone from both."""
    # Given
    other = bin_page.open_in_new_tab()
    api.send(bin_page.bin_id, path="/gone", body=b"x")
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.ask_delete_request().confirm()
    # Then
    for tab in (bin_page, other):
        expect(tab.rows).to_have_count(0)
        expect(tab.empty_state).to_be_visible()


def test_given_dont_ask_again_ticked_when_user_deletes_the_next_request_then_no_dialog_shows(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given "Don't ask again" was ticked on a request delete, when the next one is deleted, then no dialog asks."""
    # Given
    api.send(bin_page.bin_id, path="/first", body=b"x")
    api.send(bin_page.bin_id, path="/second", body=b"x")
    expect(bin_page.rows).to_have_count(2)
    bin_page.ask_delete_request().confirm(dont_ask_again=True)
    expect(bin_page.rows).to_have_count(1)
    # When
    dialog = bin_page.ask_delete_request()
    # Then
    expect(bin_page.rows).to_have_count(0)
    expect(dialog.dialog).to_be_hidden()


def test_given_bin_with_requests_when_user_clears_it_then_the_list_is_empty_but_the_bin_stays(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a bin with three requests, when the user clears it, then none are left and the bin keeps its URL."""
    # Given
    for path in ("/a", "/b", "/c"):
        api.send(bin_page.bin_id, path=path, body=b"x")
    expect(bin_page.rows).to_have_count(3)
    # When
    bin_page.ask_clear().confirm()
    # Then
    expect(bin_page.text("Cleared the bin.")).to_be_visible()
    expect(bin_page.empty_state).to_be_visible()
    assert api.send(bin_page.bin_id, body=b"x").status_code == 200


def test_given_bin_open_in_two_tabs_when_user_deletes_it_then_home_drops_it_and_the_other_tab_says_so(
    home: HomePage,
) -> None:
    """Given a bin open in two tabs, when it is deleted, then home drops it and the other tab says it was deleted."""
    # Given
    bin_page = home.goto().make_bin("doomed")
    other = bin_page.open_in_new_tab()
    # When
    bin_page.ask_delete_bin().confirm()
    # Then
    home.wait_until_loaded()
    expect(home.text("Deleted the bin.")).to_be_visible()
    expect(home.row("doomed")).to_have_count(0)
    expect(other.text("This bin was deleted.")).to_be_visible()


def test_given_delete_dialog_when_user_cancels_then_the_request_stays(bin_page: BinPage, api: StudioApi) -> None:
    """Given the delete dialog for a request, when the user cancels, then the request stays."""
    # Given
    api.send(bin_page.bin_id, path="/kept", body=b"x")
    expect(bin_page.rows).to_have_count(1)
    dialog = bin_page.ask_delete_request()
    # When
    dialog.cancel()
    # Then
    expect(bin_page.rows).to_have_count(1)
