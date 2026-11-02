"""Browser tests for a bin's reply: status, headers, body and delay."""

import threading
import time
from typing import TYPE_CHECKING

import httpx
from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage


def test_given_reply_set_to_418_with_a_header_and_body_when_request_arrives_then_sender_gets_them(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given the reply set to 418 with a header and a body, when a request arrives, then the sender gets all three."""
    # Given
    dialog = bin_page.open_reply_settings()
    dialog.set_status(418)
    dialog.add_header("X-Tea", "yes")
    dialog.set_body("short and stout")
    dialog.save()
    expect(bin_page.text("Saved the reply settings.")).to_be_visible()
    # When
    reply = api.send(bin_page.bin_id, body=b"x")
    # Then
    assert (reply.status_code, reply.headers["x-tea"], reply.text) == (418, "yes", "short and stout")


def test_given_reply_header_set_cookie_when_user_saves_then_an_error_shows_and_the_dialog_stays(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a Set-Cookie reply header, when the user saves, then an error shows, the dialog stays, nothing changes."""
    # Given
    dialog = bin_page.open_reply_settings()
    dialog.add_header("Set-Cookie", "a=b")
    # When
    dialog.save()
    # Then
    expect(dialog.error).to_have_text("A reply may not set Set-Cookie.")
    expect(dialog.dialog).to_be_visible()
    assert api.send(bin_page.bin_id, body=b"x").status_code == 200


def test_given_two_second_delay_when_request_arrives_then_page_shows_it_before_the_reply(
    bin_page: BinPage, api: StudioApi
) -> None:
    """Given a bin with a 2 s delay, when a request arrives, then the page shows it before the sender gets a reply."""
    # Given
    api.set_reply(bin_page.bin_id, delay_ms=2000)
    answered: list[float] = []

    def post() -> None:
        httpx.post(api.capture_url(bin_page.bin_id, "/slow"), content=b"x", timeout=10)
        answered.append(time.monotonic())

    sender = threading.Thread(target=post)
    # When
    sender.start()
    expect(bin_page.rows).to_have_count(1, timeout=1500)
    shown = time.monotonic()
    sender.join()
    # Then
    assert answered
    assert shown < answered[0]
