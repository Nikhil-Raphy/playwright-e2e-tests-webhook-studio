"""Browser tests for replaying a request, in both replay modes, and copying it as curl."""

from typing import TYPE_CHECKING

import pytest
from playwright.sync_api import Page, expect

from webhook_studio_e2e.pages import BinPage

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.settings import Settings


def test_given_restricted_mode_when_user_replays_to_loopback_then_the_tab_says_not_allowed(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given `restricted` mode, when the user replays to 127.0.0.1, then the Replay tab says the address is refused."""
    # Given
    api.send(bin_page.bin_id, path="/r", body=b"x")
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.replay("http://127.0.0.1:9/")
    # Then
    expect(bin_page.replay_error).to_have_text("Target address not allowed.")
    expect(bin_page.replay_result).to_have_count(0)


def test_given_local_mode_when_user_replays_to_the_echo_service_then_the_tab_shows_what_it_got(
    page: Page, settings: Settings, local_api: StudioApi
) -> None:
    """Given `local` mode, when replayed to the echo service, then its 201 reply shows the method, body and query."""
    # Given
    bin_page = BinPage(page, local_api.base_url).goto(local_api.create_bin("local replay"))
    local_api.send(bin_page.bin_id, method="PUT", path="/orig?x=1", body=b'{"a": 1}')
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.replay(f"{settings.echo_url}/hook")
    # Then
    expect(bin_page.replay_status).to_have_text("201 Created")
    expect(bin_page.replay_result).to_contain_text('"method": "PUT"')
    expect(bin_page.replay_result).to_contain_text('"path": "/hook?x=1"')
    expect(bin_page.replay_result).to_contain_text('"body": "{\\"a\\": 1}"')


def test_given_local_mode_when_user_replays_without_the_query_then_the_echo_service_gets_none(
    page: Page, settings: Settings, local_api: StudioApi
) -> None:
    """Given `local` mode, when replayed with "Use original query string" off, then the target gets no query."""
    # Given
    bin_page = BinPage(page, local_api.base_url).goto(local_api.create_bin("no query"))
    local_api.send(bin_page.bin_id, path="/orig?x=1", body=b"x")
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.replay(f"{settings.echo_url}/plain", keep_query=False)
    # Then
    expect(bin_page.replay_status).to_have_text("201 Created")
    expect(bin_page.replay_result).to_contain_text('"path": "/plain"')


@pytest.mark.only_browser("chromium")
def test_given_request_when_user_copies_it_as_curl_then_the_command_sends_it_to_this_bin(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a request, when the user presses Copy as curl, then the clipboard holds a command aimed at this bin."""
    # Given
    bin_page.allow_clipboard()
    api.send(bin_page.bin_id, method="PATCH", path="/items/4", body=b"it's")
    expect(bin_page.rows).to_have_count(1)
    # When
    bin_page.button("Copy as curl").click()
    # Then
    expect(bin_page.text("Copied as curl.")).to_be_visible()
    command = bin_page.clipboard_text()
    assert command.startswith(f"curl -X PATCH {api.capture_url(bin_page.bin_id, '/items/4')}")
    assert "--data-raw 'it'\"'\"'s'" in command
