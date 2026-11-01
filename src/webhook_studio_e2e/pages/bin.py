"""A bin's page: its capture URL, the requests it caught, and the actions on them."""

from typing import TYPE_CHECKING, Self
from urllib.parse import urlsplit

from playwright.sync_api import expect

from webhook_studio_e2e.pages.base import AppPage
from webhook_studio_e2e.pages.dialogs import ConfirmDialog, ReplyDialog

if TYPE_CHECKING:
    from playwright.sync_api import Download, Locator, Page

LIVE = "Live"
CLIPBOARD = ("clipboard-read", "clipboard-write")


class BinPage(AppPage):  # pylint: disable=too-many-public-methods  # One method per user action on the app's main page.
    """The page at `/bins/{bin_id}`."""

    def __init__(self, page: Page, base_url: str) -> None:
        """Find the page's parts.

        Args:
            page: The browser page.
            base_url: The app's address.
        """
        super().__init__(page, base_url)
        self.status: Locator = page.get_by_test_id("status")
        self.label: Locator = page.get_by_test_id("bin-label")
        self.capture_url: Locator = page.get_by_test_id("capture-url")
        self.empty_state: Locator = page.get_by_test_id("empty-state")
        self.rows: Locator = page.get_by_test_id("request-row")
        self.request_count: Locator = page.get_by_test_id("request-count")
        self.method_filter: Locator = page.get_by_role("combobox", name="Filter by method")
        self.search_box: Locator = page.get_by_placeholder("Search")
        self.load_older_button: Locator = page.get_by_role("button", name="Load older")
        self.masked_headers: Locator = page.get_by_test_id("masked-header")
        self.tab_panel: Locator = page.get_by_role("tabpanel")
        self.names: Locator = self.tab_panel.get_by_role("rowheader")
        self.values: Locator = self.tab_panel.get_by_role("cell")
        self.body: Locator = page.get_by_test_id("body")
        self.replay_target: Locator = page.get_by_placeholder("https://example.com/hook")
        self.replay_status: Locator = page.get_by_test_id("replay-status")
        self.replay_result: Locator = page.get_by_test_id("replay-result")
        self.replay_error: Locator = page.get_by_test_id("replay-error")

    @property
    def bin_id(self) -> str:
        """The id of the bin on show, read from the address bar.

        Returns:
            The bin id.
        """
        return urlsplit(self.page.url).path.rstrip("/").rsplit("/", 1)[-1]

    def goto(self, bin_id: str) -> Self:
        """Open a bin's page and wait until it follows the bin live.

        Args:
            bin_id: The bin id.

        Returns:
            This page.
        """
        return self.open(bin_id).wait_until_live()

    def open(self, bin_id: str) -> Self:
        """Open a bin's page without waiting for it, as for an id that no bin has.

        Args:
            bin_id: The bin id.

        Returns:
            This page.
        """
        self.page.goto(f"{self.base_url}/bins/{bin_id}")
        return self

    def open_in_new_tab(self) -> BinPage:
        """Open this bin in a second tab of the same browser and wait until that tab follows it live.

        Returns:
            The second tab's page.
        """
        return BinPage(self.page.context.new_page(), self.base_url).goto(self.bin_id)

    def reload(self) -> Self:
        """Reload the page and wait until it follows the bin live again.

        Returns:
            This page.
        """
        self.page.reload()
        return self.wait_until_live()

    def wait_until_live(self) -> Self:
        """Wait until the page has loaded and its status dot says Live.

        Returns:
            This page.
        """
        expect(self.spinner).to_have_count(0)
        expect(self.status).to_have_text(LIVE)
        return self

    def button(self, name: str) -> Locator:
        """Find a button by its exact text.

        Args:
            name: The button's text.

        Returns:
            The button.
        """
        return self.page.get_by_role("button", name=name, exact=True)

    def row(self, path: str) -> Locator:
        """Find the list row of the request sent to one sub-path.

        Args:
            path: The sub-path, such as "/github".

        Returns:
            The row.
        """
        return self.rows.filter(has_text=path)

    def open_tab(self, name: str) -> None:
        """Show one tab of the request on show.

        Args:
            name: The tab's name: Overview, Headers, Query, Body or Replay.
        """
        self.page.get_by_role("tab", name=name).click()

    def field(self, name: str) -> Locator:
        """Find the value beside one name in the tab on show, such as "Path" in the Overview tab.

        Args:
            name: The field's name, as its row header shows it.

        Returns:
            The value's cell.
        """
        header = self.page.get_by_role("rowheader", name=name, exact=True)
        return self.tab_panel.get_by_role("row").filter(has=header).get_by_role("cell")

    def press_load_older(self) -> None:
        """Press "Load older" without scrolling to it.

        Scrolling the button into view would let the list's scroll trigger load first; a dispatched click tests the
        button alone, as a keyboard or screen-reader user would reach it.
        """
        self.load_older_button.dispatch_event("click")

    def filter_by_method(self, method: str) -> None:
        """List only requests with one method.

        Args:
            method: The method, or "All methods".
        """
        self.method_filter.click()
        self.page.get_by_role("option", name=method, exact=True).click()

    def search(self, text: str) -> None:
        """Type into the search box.

        Args:
            text: The text to find.
        """
        self.search_box.fill(text)

    def allow_clipboard(self) -> None:
        """Let pages in this browser read and write the clipboard; only Chromium allows the read."""
        self.page.context.grant_permissions(CLIPBOARD)

    def clipboard_text(self) -> str:
        """Read the clipboard, as the page sees it.

        Returns:
            The text on the clipboard.
        """
        return str(self.page.evaluate("navigator.clipboard.readText()"))

    def ask_delete_request(self) -> ConfirmDialog:
        """Press "Delete request".

        Returns:
            The confirmation dialog, which shows unless this browser chose not to be asked.
        """
        self.button("Delete request").click()
        return ConfirmDialog(self.page)

    def ask_clear(self) -> ConfirmDialog:
        """Press "Clear".

        Returns:
            The confirmation dialog.
        """
        self.button("Clear").click()
        return ConfirmDialog(self.page)

    def ask_delete_bin(self) -> ConfirmDialog:
        """Press "Delete bin".

        Returns:
            The confirmation dialog.
        """
        self.button("Delete bin").click()
        return ConfirmDialog(self.page)

    def open_reply_settings(self) -> ReplyDialog:
        """Press "Reply settings" and wait for the dialog.

        Returns:
            The dialog.
        """
        self.button("Reply settings").click()
        dialog = ReplyDialog(self.page)
        expect(dialog.dialog).to_be_visible()
        return dialog

    def export(self) -> Download:
        """Press "Export" and wait for the file.

        Returns:
            The download.
        """
        with self.page.expect_download() as download:
            self.page.get_by_role("link", name="Export").click()
        return download.value

    def download_body(self) -> Download:
        """Press "Download" on the Body tab of a binary request and wait for the file.

        Returns:
            The download.
        """
        with self.page.expect_download() as download:
            self.button("Download").click()
        return download.value

    def replay(self, target: str, *, keep_query: bool = True) -> None:
        """Send the request on show to another address from the Replay tab.

        Args:
            target: The address to send it to.
            keep_query: Whether to add the original query string to the address.
        """
        self.open_tab("Replay")
        self.replay_target.fill(target)
        if not keep_query:
            switch = self.page.get_by_role("switch", name="Use original query string")
            switch.click()
            expect(switch).not_to_be_checked()
        self.button("Send").click()
