"""Tests for the echo server that replay tests send requests to."""

import json
import threading
from http.server import ThreadingHTTPServer
from typing import TYPE_CHECKING

import httpx

from webhook_studio_e2e import echo
from webhook_studio_e2e.echo import EchoServer

if TYPE_CHECKING:
    import pytest


def test_given_echo_server_when_request_arrives_then_reply_holds_what_was_sent() -> None:
    """Given a running echo server, when a request arrives, then the 201 reply holds its method, path, headers, body."""
    # Given
    with EchoServer() as server:
        # When
        reply = httpx.put(f"{server.url}/hook?x=1", content=b'{"a": 1}', headers={"X-Sig": "abc"})
    # Then
    echoed = json.loads(reply.content)
    assert (reply.status_code, reply.headers["x-echo"]) == (201, "yes")
    assert (echoed["method"], echoed["path"], echoed["body"]) == ("PUT", "/hook?x=1", '{"a": 1}')
    assert ["x-sig", "abc"] in echoed["headers"]


def test_given_echo_server_when_head_arrives_then_reply_has_no_body() -> None:
    """Given a running echo server, when a HEAD request arrives, then the reply is 201 with no body."""
    # Given
    with EchoServer() as server:
        # When
        reply = httpx.head(server.url)
    # Then
    assert (reply.status_code, reply.content) == (201, b"")


def test_given_port_argument_when_main_runs_then_it_serves_on_that_port(monkeypatch: pytest.MonkeyPatch) -> None:
    """Given `--port 0`, when the command runs, then it binds a server and serves until stopped."""
    # Given
    served = threading.Event()
    monkeypatch.setattr(ThreadingHTTPServer, "serve_forever", lambda _server: served.set())
    # When
    echo.main(["--host", "127.0.0.1", "--port", "0"])
    # Then
    assert served.is_set()
