"""A small client for Webhook Studio's REST API, so tests make their data in milliseconds instead of through pages."""

from typing import TYPE_CHECKING, Any, Self, TypedDict, Unpack

import httpx

if TYPE_CHECKING:
    from collections.abc import Mapping
    from types import TracebackType

TIMEOUT_S = 10.0
CAPTURE_PREFIX = "/api/webhook"
BINS = "/api/v1/bins"
VERSION = "/api/v1/version"

type Headers = Mapping[str, str] | list[tuple[str, str]]


class Reply(TypedDict, total=False):
    """What a bin sends back; a field left out keeps the app's default.

    Attributes:
        status: The HTTP status code.
        content_type: The `Content-Type`, or None for the default.
        headers: Extra headers, as name and value pairs.
        body: The body text, or None for the app's default JSON body.
        delay_ms: How long to wait before replying, in milliseconds.
    """

    status: int
    content_type: str | None
    headers: list[tuple[str, str]]
    body: str | None
    delay_ms: int


class StudioApi:
    """Calls one Webhook Studio instance: makes bins, sends requests to them, and changes or deletes them."""

    def __init__(self, base_url: str, *, transport: httpx.BaseTransport | None = None) -> None:
        """Open a client for one app.

        Args:
            base_url: The app's address, such as http://localhost:17300.
            transport: Where requests go; tests of this class pass a fake one.
        """
        self.base_url = base_url.rstrip("/")
        self._client = httpx.Client(base_url=self.base_url, timeout=TIMEOUT_S, transport=transport)

    def __enter__(self) -> Self:
        """Use the client in a `with` block.

        Returns:
            The client.
        """
        return self

    def __exit__(
        self, exc_type: type[BaseException] | None, exc: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """Close the client at the end of the `with` block.

        Args:
            exc_type: The type of the exception that ended the block, if any.
            exc: The exception, if any.
            traceback: Its traceback, if any.
        """
        self.close()

    def close(self) -> None:
        """Close the client's connections."""
        self._client.close()

    def capture_url(self, bin_id: str, path: str = "") -> str:
        """Build the URL that senders use for a bin.

        Args:
            bin_id: The bin id.
            path: A sub-path, starting with "/", or empty.

        Returns:
            The full capture URL.
        """
        return f"{self.base_url}{CAPTURE_PREFIX}/{bin_id}{path}"

    def version(self) -> str:
        """Read the app's version.

        Returns:
            The version, such as "1.2.0".
        """
        return str(self._json(self._client.get(VERSION))["version"])

    def create_bin(self, label: str | None = None) -> str:
        """Make a bin.

        Args:
            label: The bin's label, or None for no label.

        Returns:
            The new bin's id.
        """
        body = {} if label is None else {"label": label}
        return str(self._json(self._client.post(BINS, json=body))["id"])

    def send(
        self,
        bin_id: str,
        *,
        method: str = "POST",
        path: str = "",
        body: bytes = b"",
        headers: Headers | None = None,
    ) -> httpx.Response:
        """Send one request to a bin, as a webhook sender would.

        Args:
            bin_id: The bin id.
            method: The HTTP method.
            path: A sub-path, starting with "/", which may hold a query string.
            body: The body bytes.
            headers: Extra request headers.

        Returns:
            The bin's reply, whatever its status.
        """
        return self._client.request(method, f"{CAPTURE_PREFIX}/{bin_id}{path}", content=body, headers=headers)

    def rename(self, bin_id: str, label: str | None) -> None:
        """Change a bin's label.

        Args:
            bin_id: The bin id.
            label: The new label, or None to clear it.
        """
        self._json(self._client.patch(f"{BINS}/{bin_id}", json={"label": label}))

    def set_reply(self, bin_id: str, **reply: Unpack[Reply]) -> None:
        """Change what a bin sends back to senders.

        Args:
            bin_id: The bin id.
            **reply: The reply fields to set.
        """
        self._json(self._client.patch(f"{BINS}/{bin_id}", json={"reply": reply}))

    def delete_bin(self, bin_id: str) -> None:
        """Delete a bin and its requests.

        Args:
            bin_id: The bin id.
        """
        self._client.delete(f"{BINS}/{bin_id}").raise_for_status()

    @staticmethod
    def _json(response: httpx.Response) -> Any:  # noqa: ANN401  # JSON bodies hold any shape.
        """Fail on an error status, else read the JSON body."""
        response.raise_for_status()
        return response.json()
