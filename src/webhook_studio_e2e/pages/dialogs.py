"""The dialogs on a bin's page: the delete confirmation and the reply settings."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page


class ConfirmDialog:
    """Asks before a request, every request or the bin is deleted."""

    def __init__(self, page: Page) -> None:
        """Find the dialog's parts.

        Args:
            page: The browser page that shows the dialog.
        """
        self.dialog: Locator = page.get_by_role("alertdialog")
        self.dont_ask: Locator = self.dialog.get_by_role("checkbox", name="Don't ask again")
        self.confirm_button: Locator = self.dialog.get_by_test_id("confirm-delete")
        self.cancel_button: Locator = self.dialog.get_by_role("button", name="Cancel")

    def confirm(self, *, dont_ask_again: bool = False) -> None:
        """Delete, optionally ticking "Don't ask again" first.

        Args:
            dont_ask_again: Whether to tick the box, so this kind of delete stops asking in this browser.
        """
        expect(self.dialog).to_be_visible()
        if dont_ask_again:
            # The app sets the box from its server, so wait for the round trip rather than use check().
            self.dont_ask.click()
            expect(self.dont_ask).to_be_checked()
        self.confirm_button.click()
        expect(self.dialog).to_be_hidden()

    def cancel(self) -> None:
        """Close the dialog without deleting anything."""
        self.cancel_button.click()
        expect(self.dialog).to_be_hidden()


class ReplyDialog:
    """Sets what a bin sends back to each sender."""

    def __init__(self, page: Page) -> None:
        """Find the dialog's parts.

        Args:
            page: The browser page that shows the dialog.
        """
        self.dialog: Locator = page.get_by_role("dialog", name="Reply settings")
        self.status: Locator = self.dialog.get_by_label("Status")
        self.custom_body: Locator = self.dialog.get_by_role("switch", name="Custom body")
        self.body: Locator = self.dialog.get_by_role("textbox", name="Custom body")
        self.error: Locator = self.dialog.get_by_test_id("reply-error")
        self.save_button: Locator = self.dialog.get_by_role("button", name="Save")

    def set_status(self, status: int) -> None:
        """Type the reply status.

        Args:
            status: The HTTP status code.
        """
        self.status.fill(str(status))

    def add_header(self, name: str, value: str) -> None:
        """Add one reply header.

        Args:
            name: The header name.
            value: The header value.
        """
        self.dialog.get_by_role("button", name="Add header").click()
        self.dialog.get_by_placeholder("Name").last.fill(name)
        self.dialog.get_by_placeholder("Value").last.fill(value)

    def set_body(self, body: str) -> None:
        """Send a body of our own instead of the default JSON.

        Args:
            body: The body text.
        """
        self.custom_body.click()
        expect(self.custom_body).to_be_checked()
        self.body.fill(body)

    def save(self) -> None:
        """Save the settings; the dialog closes when they are valid and stays open with an error when not."""
        self.save_button.click()
