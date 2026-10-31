"""An HTTP server that answers every request with what it received, as the target for replay tests.

Run it with `python -m webhook_studio_e2e.echo --port 8080`.
"""

import argparse
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import TYPE_CHECKING, Self, override

if TYPE_CHECKING:
    from collections.abc import Sequence
    from types import TracebackType

DEFAULT_PORT = 8080
ECHO_HEADER = ("X-Echo", "yes")


class EchoHandler(BaseHTTPRequestHandler):
    """Replies 201 with a JSON body that holds the method, path, headers and body text it got."""

    def _echo(self) -> None:
        """Read the request and reply with what it held, with no body for HEAD."""
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length) if length else b""
        reply = json.dumps(
            {
                "method": self.command,
                "path": self.path,
                "headers": [[name.lower(), value] for name, value in self.headers.items()],
                "body": body.decode("utf-8", errors="replace"),
            },
            indent=2,
        ).encode()
        self.send_response(HTTPStatus.CREATED)
        self.send_header("Content-Type", "application/json")
        self.send_header(*ECHO_HEADER)
        self.send_header("Content-Length", str(len(reply)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(reply)

    # http.server looks up one method per HTTP method name.
    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_OPTIONS = do_HEAD = _echo  # noqa: N815

    @override
    def log_message(self, format: str, *args: object) -> None:  # http.server names the first argument `format`.
        """Keep test output quiet."""


class EchoServer:
    """Runs the echo handler on a background thread, for tests in this repo."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        """Bind the server.

        Args:
            host: The address to listen on.
            port: The port; 0 picks a free one.
        """
        self._server = ThreadingHTTPServer((host, port), EchoHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        """The server's base URL.

        Returns:
            The URL, such as http://127.0.0.1:41235.
        """
        host, port = self._server.server_address[:2]
        return f"http://{host!s}:{port}"

    def __enter__(self) -> Self:
        """Start serving.

        Returns:
            The running server.
        """
        self._thread.start()
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """Stop serving and close the socket.

        Args:
            exc_type: The type of the exception that ended the block, if any.
            exc: The exception, if any.
            traceback: Its traceback, if any.
        """
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()


def main(argv: Sequence[str] | None = None) -> None:
    """Serve until stopped.

    Args:
        argv: The command-line arguments; None reads them from the process.
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default="0.0.0.0", help="address to listen on (default: all)")  # noqa: S104
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port (default: {DEFAULT_PORT})")
    options = parser.parse_args(argv)
    with ThreadingHTTPServer((options.host, options.port), EchoHandler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
