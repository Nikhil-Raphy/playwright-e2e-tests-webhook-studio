"""Browser tests for finding requests: the method filter, search, Clear filters and loading older requests."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage

PAGE_SIZE = 50


def test_given_get_and_post_requests_when_user_filters_by_post_then_only_post_shows(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a bin with GET and POST requests, when the user filters by POST, then only POST requests show."""
    # Given
    api.send(bin_page.bin_id, method="GET", path="/one")
    api.send(bin_page.bin_id, method="POST", path="/two", body=b"x")
    expect(bin_page.rows).to_have_count(2)
    # When
    bin_page.filter_by_method("POST")
    # Then
    expect(bin_page.rows).to_have_count(1)
    expect(bin_page.rows).to_contain_text("/two")


def test_given_invoice_body_when_user_searches_invoice_then_that_request_shows(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a request whose body holds "invoice", when the user searches "INVOICE", then only that request shows."""
    # Given
    api.send(bin_page.bin_id, path="/order", body=b'{"kind": "order"}')
    api.send(bin_page.bin_id, path="/bill", body=b'{"kind": "invoice"}')
    expect(bin_page.rows).to_have_count(2)
    # When
    bin_page.search("INVOICE")
    # Then
    expect(bin_page.rows).to_have_count(1)
    expect(bin_page.rows).to_contain_text("/bill")
    expect(bin_page.request_count).to_contain_text("1 matching")


def test_given_filters_on_when_user_clears_them_then_every_request_shows_again(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a method filter and a search that match nothing, when the user clears them, then every request shows."""
    # Given
    api.send(bin_page.bin_id, method="GET", path="/a")
    api.send(bin_page.bin_id, method="PUT", path="/b", body=b"x")
    bin_page.filter_by_method("DELETE")
    bin_page.search("nothing")
    expect(bin_page.text("No requests match.")).to_be_visible()
    # When
    bin_page.button("Clear filters").click()
    # Then
    expect(bin_page.rows).to_have_count(2)
    expect(bin_page.search_box).to_have_value("")
    expect(bin_page.method_filter).to_have_text("All methods")


def test_given_more_than_a_page_when_user_scrolls_to_the_end_then_older_requests_load(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given 60 requests, when the user scrolls to the end of the list, then all 60 show and nothing older is left."""
    # Given
    for number in range(60):
        api.send(bin_page.bin_id, path=f"/n{number}", body=b"x")
    bin_page.reload()
    expect(bin_page.rows).to_have_count(PAGE_SIZE)
    # When
    bin_page.rows.last.scroll_into_view_if_needed()
    # Then
    expect(bin_page.rows).to_have_count(60)
    expect(bin_page.load_older_button).to_have_count(0)


def test_given_more_than_a_page_when_user_presses_load_older_then_the_rest_load(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given 60 requests, when the user presses "Load older" instead of scrolling, then all 60 show and it goes."""
    # Given
    for number in range(60):
        api.send(bin_page.bin_id, path=f"/n{number}", body=b"x")
    bin_page.reload()
    expect(bin_page.rows).to_have_count(PAGE_SIZE)
    # When
    bin_page.press_load_older()
    # Then
    expect(bin_page.rows).to_have_count(60)
    expect(bin_page.load_older_button).to_have_count(0)
