"""Browser tests for a bin's page: its URL, the empty state, and each tab of the request on show."""

from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage

BINARY = {"content-type": "application/octet-stream"}
TEXT = {"content-type": "text/plain"}


def test_given_new_bin_when_its_page_opens_then_it_shows_how_to_send_a_request(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a new bin, when its page opens, then it waits for requests and shows a curl command for its URL."""
    # Given
    capture_url = api.capture_url(bin_page.bin_id)
    # When
    empty_state = bin_page.empty_state
    # Then
    expect(empty_state).to_contain_text("Waiting for requests")
    expect(empty_state).to_contain_text(f"curl -X POST {capture_url}")
    expect(bin_page.capture_url).to_have_text(capture_url)


@pytest.mark.only_browser("chromium")
def test_given_bin_when_user_copies_its_url_then_the_clipboard_holds_it(bin_page: BinPage, api: StudioApi) -> None:
    """Given a bin, when the user presses Copy URL, then the clipboard holds the bin's URL and a toast says so."""
    # Given
    bin_page.allow_clipboard()
    # When
    bin_page.button("Copy URL").click()
    # Then
    expect(bin_page.text("Copied the bin URL.")).to_be_visible()
    assert bin_page.clipboard_text() == api.capture_url(bin_page.bin_id)


def test_given_new_bin_when_client_sends_json_then_body_tab_shows_formatted_json(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a new bin, when a client sends JSON, then the request is listed and the Body tab shows formatted JSON."""
    # Given
    body = b'{"event":"push","ids":[1,2]}'
    # When
    api.send(bin_page.bin_id, path="/github", body=body, headers={"content-type": "application/json"})
    bin_page.open_tab("Body")
    # Then
    expect(bin_page.rows).to_have_count(1)
    expect(bin_page.body).to_contain_text('"event": "push"')


def test_given_authorization_header_when_headers_open_then_value_is_masked_until_clicked(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a request with an Authorization header, when Headers opens, then the value shows as dots until clicked."""
    # Given
    api.send(bin_page.bin_id, body=b"{}", headers={"Authorization": "Bearer s3cret"})
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Headers")
    # Then
    expect(bin_page.masked_headers).to_have_text("••••")
    expect(bin_page.text("Bearer s3cret")).to_have_count(0)
    bin_page.masked_headers.click()
    expect(bin_page.text("Bearer s3cret")).to_be_visible()


def test_given_repeated_query_keys_when_query_tab_opens_then_every_pair_shows_in_order(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a query string with a repeated key, when the Query tab opens, then every pair shows in order."""
    # Given
    api.send(bin_page.bin_id, method="GET", path="/search?x=1&x=2&y=z")
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Query")
    # Then
    expect(bin_page.names).to_have_text(["x", "x", "y"])
    expect(bin_page.values).to_have_text(["1", "2", "z"])


def test_given_form_body_when_body_tab_opens_then_each_field_shows(bin_page: BinPage, api: StudioApi) -> None:
    """Given a form body, when the Body tab opens, then each field shows as a name and a value."""
    # Given
    headers = {"content-type": "application/x-www-form-urlencoded"}
    api.send(bin_page.bin_id, path="/form", body=b"name=Ada&role=admin", headers=headers)
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Body")
    # Then
    expect(bin_page.names).to_have_text(["name", "role"])
    expect(bin_page.values).to_have_text(["Ada", "admin"])


def test_given_text_request_with_a_query_when_overview_shows_then_each_field_holds_its_value(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a text request with a query, when the Overview tab shows, then each field holds the request's value."""
    # Given
    sent = api.send(bin_page.bin_id, path="/orders?x=1", body=b"hello", headers=TEXT)
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Overview")
    # Then
    expected = {
        "Request id": sent.json()["request_id"],
        "Method": "POST",
        "Path": "/orders",
        "Query string": "x=1",
        "Content type": "text/plain",
        "Body size": "5 bytes",
        "HTTP version": "1.1",
        "Reply status": "200",
    }
    for name, value in expected.items():
        expect(bin_page.field(name)).to_have_text(value)


def test_given_text_body_over_two_lines_when_body_tab_opens_then_it_shows_as_text_with_its_lines(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a plain-text body over two lines, when the Body tab opens, then it shows as text, line break kept."""
    # Given
    api.send(bin_page.bin_id, path="/note", body=b"hello\nworld", headers=TEXT)
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Body")
    # Then
    expect(bin_page.body).to_contain_text("world")
    assert bin_page.body.inner_text().strip() == "hello\nworld"


def test_given_binary_body_when_body_opens_then_size_and_download_show(bin_page: BinPage, api: StudioApi) -> None:
    """Given a binary body, when the Body tab opens, then it shows the size and a download of the exact bytes."""
    # Given
    body = bytes(range(256))
    api.send(bin_page.bin_id, method="PUT", path="/blob", body=body, headers=BINARY)
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.open_tab("Body")
    download = bin_page.download_body()
    # Then
    expect(bin_page.body).to_contain_text("Binary body, 256 bytes.")
    assert download.path().read_bytes() == body
