"""Page objects: one class per page or dialog, so tests read as user steps and hold no locators."""

from webhook_studio_e2e.pages.base import SCREENSHOT_MASKS, AppPage
from webhook_studio_e2e.pages.bin import BinPage
from webhook_studio_e2e.pages.dialogs import ConfirmDialog, ReplyDialog
from webhook_studio_e2e.pages.home import HomePage

__all__ = ["SCREENSHOT_MASKS", "AppPage", "BinPage", "ConfirmDialog", "HomePage", "ReplyDialog"]
