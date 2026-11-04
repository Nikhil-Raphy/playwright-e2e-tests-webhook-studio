"""Tests for the REST client, against a fake transport that records each call."""

# Tests take the fixture as an argument of the same name.
# pylint: disable=redefined-outer-name

import json

import httpx
import pytest

from webhook_studio_e2e.api import StudioApi

BIN_ID = "AbCdEfGhIjKlMnOpQrStUv"
VERSION = "1.2.0"


class FakeApp:  # pylint: disable=too-few-public-methods  # httpx calls it as a function.
    """Answers like Webhook Studio and keeps every request it gets."""

    def __init__(self) -> None:
        """Start with no requests."""
        self.received: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        """Answer one request.

        Args:
            request: The request.

        Returns:
            A reply shaped like the app's.
        """
        self.received.append(request)
        path = request.url.path
        if request.method == "POST" and path == "/api/v1/bins":
            return httpx.Response(201, json={"id": BIN_ID})
        if path == "/api/v1/version":
            return httpx.Response(200, json={"version": VERSION})
        if path == f"/api/v1/bins/{BIN_ID}":
            return httpx.Response(204) if request.method == "DELETE" else httpx.Response(200, json={"id": BIN_ID})
        if path.startswith(f"/api/webhook/{BIN_ID}"):
            return httpx.Response(200, json={"ok": True})
        return httpx.Response(404, json={"detail": "Not found."})


@pytest.fixture
def app() -> FakeApp:
    """Give each test its own fake app.

    Returns:
        The fake app.
    """
    return FakeApp()


def test_given_label_or_none_when_bins_are_made_then_each_post_carries_it_and_the_id_returns(app: FakeApp) -> None:
    """Given a label and then none, when bins are made, then each POST body matches and the new id comes back."""
    # Given
    with StudioApi("http://studio/", transport=httpx.MockTransport(app)) as api:
        # When
        ids = [api.create_bin("orders"), api.create_bin()]
    # Then
    assert ids == [BIN_ID, BIN_ID]
    assert [json.loads(request.content) for request in app.received] == [{"label": "orders"}, {}]


def test_given_app_when_its_version_is_read_then_the_version_route_answers_it(app: FakeApp) -> None:
    """Given an app, when its version is read, then the client asks the version route and returns its answer."""
    # Given
    with StudioApi("http://studio", transport=httpx.MockTransport(app)) as api:
        # When
        version = api.version()
    # Then
    assert version == VERSION
    assert (app.received[0].method, app.received[0].url.path) == ("GET", "/api/v1/version")


def test_given_bin_when_request_is_sent_then_it_reaches_the_capture_url_as_given(app: FakeApp) -> None:
    """Given a bin, when a request is sent to it, then the method, path, body and headers reach its capture URL."""
    # Given
    api = StudioApi("http://studio", transport=httpx.MockTransport(app))
    # When
    reply = api.send(BIN_ID, method="PUT", path="/hook?x=1", body=b"\x00", headers={"x-sig": "a"})
    api.close()
    # Then
    sent = app.received[0]
    assert reply.status_code == 200
    assert (sent.method, str(sent.url), sent.content, sent.headers["x-sig"]) == (
        "PUT",
        f"http://studio/api/webhook/{BIN_ID}/hook?x=1",
        b"\x00",
        "a",
    )
    assert api.capture_url(BIN_ID, "/x") == f"http://studio/api/webhook/{BIN_ID}/x"


def test_given_bin_when_renamed_replied_and_deleted_then_each_call_is_right(app: FakeApp) -> None:
    """Given a bin, when it is renamed, its reply set and then deleted, then each call fits."""
    # Given
    with StudioApi("http://studio", transport=httpx.MockTransport(app)) as api:
        # When
        api.rename(BIN_ID, "new")
        api.set_reply(BIN_ID, status=418, headers=[("X-Tea", "yes")], body="tea")
        api.delete_bin(BIN_ID)
    # Then
    assert [(request.method, request.content) for request in app.received[:2]] == [
        ("PATCH", b'{"label":"new"}'),
        ("PATCH", b'{"reply":{"status":418,"headers":[["X-Tea","yes"]],"body":"tea"}}'),
    ]
    assert app.received[2].method == "DELETE"


def test_given_unknown_bin_when_renamed_or_deleted_then_the_error_is_raised(app: FakeApp) -> None:
    """Given a bin the app does not know, when it is renamed or deleted, then an HTTP error rises."""
    # Given
    with StudioApi("http://studio", transport=httpx.MockTransport(app)) as api:
        # When
        with pytest.raises(httpx.HTTPStatusError) as renamed:
            api.rename("unknown", "new")
        with pytest.raises(httpx.HTTPStatusError) as deleted:
            api.delete_bin("unknown")
    # Then
    assert (renamed.value.response.status_code, deleted.value.response.status_code) == (404, 404)
