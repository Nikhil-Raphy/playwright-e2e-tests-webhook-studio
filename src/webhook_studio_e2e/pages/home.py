"""The home page: make a bin, open one, and see the bins this browser made."""

from typing import TYPE_CHECKING, Self

from playwright.sync_api import expect

from webhook_studio_e2e.pages.base import AppPage
from webhook_studio_e2e.pages.bin import BinPage

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class HomePage(AppPage):
    """The page at `/`."""

    def __init__(self, page: Page, base_url: str) -> None:
        """Find the page's parts.

        Args:
            page: The browser page.
            base_url: The app's address.
        """
        super().__init__(page, base_url)
        self.label_box: Locator = page.get_by_placeholder("Label (optional)")
        self.new_bin_button: Locator = page.get_by_role("button", name="New bin")
        self.open_box: Locator = page.get_by_placeholder("Bin id or URL")
        self.open_button: Locator = page.get_by_role("button", name="Open", exact=True)
        self.bin_rows: Locator = page.get_by_test_id("bin-row")

    def goto(self) -> Self:
        """Open the page and wait until its list has loaded.

        Returns:
            This page.
        """
        self.page.goto(f"{self.base_url}/")
        return self.wait_until_loaded()

    def reload(self) -> Self:
        """Reload the page and wait until its list has loaded again.

        Returns:
            This page.
        """
        self.page.reload()
        return self.wait_until_loaded()

    def wait_until_loaded(self) -> Self:
        """Wait until the browser shows this page, as after a bin is deleted, and its list has loaded.

        Returns:
            This page.
        """
        self.page.wait_for_url(f"{self.base_url}/")
        expect(self.spinner).to_have_count(0)
        return self

    def make_bin(self, label: str = "") -> BinPage:
        """Make a bin through the page and wait until its page follows it live.

        Args:
            label: The label to type; empty for none.

        Returns:
            The new bin's page.
        """
        self.label_box.fill(label)
        self.new_bin_button.click()
        self.page.wait_for_url("**/bins/*")
        return BinPage(self.page, self.base_url).wait_until_live()

    def open_bin(self, text: str) -> BinPage:
        """Type a bin id or URL and press Open.

        Args:
            text: What to type.

        Returns:
            The bin's page, which shows once the app finds a bin id in the text.
        """
        self.open_box.fill(text)
        self.open_button.click()
        return BinPage(self.page, self.base_url)

    def row(self, label: str) -> Locator:
        """Find the list row of one bin.

        Args:
            label: The bin's label.

        Returns:
            The row.
        """
        return self.bin_rows.filter(has_text=label)
