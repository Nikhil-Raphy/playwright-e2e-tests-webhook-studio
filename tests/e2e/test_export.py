"""Browser tests for exporting a bin as a JSON file."""

import json
from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import BinPage


def test_given_bin_when_user_exports_it_then_the_file_holds_every_request(bin_page: BinPage, api: StudioApi) -> None:
    """Given a bin with two requests, when the user exports it, then the file is in the export format with both."""
    # Given
    api.send(bin_page.bin_id, path="/a", body=b'{"a": 1}')
    api.send(bin_page.bin_id, method="PUT", path="/b", body=b"\xff")
    expect(bin_page.rows).to_have_count(2)
    # When
    download = bin_page.export()
    # Then
    document = json.loads(download.path().read_bytes())
    assert download.suggested_filename == f"webhook-studio-{bin_page.bin_id[:6]}.json"
    assert document["format"] == "webhook-studio-export"
    assert [entry["path"] for entry in document["requests"]] == ["/a", "/b"]
