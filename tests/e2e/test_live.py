"""Browser tests for live updates: requests and renames show at once, in every open tab."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage


def test_given_bin_page_open_when_request_arrives_then_it_shows_within_one_second(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a bin's page is open, when a request arrives, then it shows within 1 s with no reload."""
    # Given
    expect(bin_page.empty_state).to_be_visible()
    # When
    api.send(bin_page.bin_id, path="/first", body=b"x")
    # Then
    expect(bin_page.rows).to_have_count(1, timeout=1000)
    expect(bin_page.rows).to_contain_text("/first")


def test_given_two_tabs_on_one_bin_when_request_arrives_then_both_show_it(bin_page: BinPage, api: StudioApi) -> None:
    """Given two tabs open on one bin, when a request arrives, then both show it."""
    # Given
    other = bin_page.open_in_new_tab()
    # When
    api.send(bin_page.bin_id, body=b"x")
    # Then
    for tab in (bin_page, other):
        expect(tab.rows).to_have_count(1)


def test_given_bin_page_open_when_bin_is_renamed_through_the_api_then_the_label_changes(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a bin's page is open, when the bin is renamed through the API, then the new label shows."""
    # Given
    expect(bin_page.label).to_have_text("e2e")
    # When
    api.rename(bin_page.bin_id, "new name")
    # Then
    expect(bin_page.label).to_have_text("new name")
