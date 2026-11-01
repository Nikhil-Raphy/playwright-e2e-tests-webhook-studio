"""What every page of the app shares: the browser page, the app's address, the loading spinner and visible text."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Locator, Page

SCREENSHOT_MASKS = (
    '[data-testid="capture-url"]',
    "time",
    '[data-testid="bin-row"] code',
    '[data-testid="empty-state"] pre',
)
"""Parts that differ on every run: bin URLs and ids, the curl command that holds them, and relative times."""


class AppPage:
    """The parts and actions that the home page and a bin's page share."""

    def __init__(self, page: Page, base_url: str) -> None:
        """Find the shared parts.

        Args:
            page: The browser page.
            base_url: The app's address.
        """
        self.page = page
        self.base_url = base_url
        self.spinner: Locator = page.get_by_test_id("loading")

    def text(self, content: str) -> Locator:
        """Find text the page shows, such as a toast, a notice or a header value.

        Args:
            content: The text, or part of it.

        Returns:
            The elements that show it.
        """
        return self.page.get_by_text(content)

    def move_mouse_away(self) -> None:
        """Move the mouse to the top-left corner, so no hover style lands in a screenshot."""
        self.page.mouse.move(0, 0)
