"""Browser tests for the home page: make a bin, open one, and see the bins this browser made."""

from typing import TYPE_CHECKING

from playwright.sync_api import expect

if TYPE_CHECKING:
    from webhook_studio_e2e.api import StudioApi
    from webhook_studio_e2e.pages import HomePage


def test_given_label_when_user_makes_a_bin_then_its_page_opens_with_that_label(home: HomePage) -> None:
    """Given a label, when the user makes a bin, then the bin's page opens live, with the label and its URL."""
    # Given
    home.goto()
    # When
    bin_page = home.make_bin("orders")
    # Then
    expect(bin_page.label).to_have_text("orders")
    expect(bin_page.capture_url).to_have_text(f"{home.base_url}/api/webhook/{bin_page.bin_id}")


def test_given_bin_id_when_user_opens_it_then_the_bin_page_shows(home: HomePage, api: StudioApi) -> None:
    """Given a bin's bare id, when the user opens it from the home page, then the bin's page shows."""
    # Given
    bin_id = api.create_bin("opened by id")
    home.goto()
    # When
    bin_page = home.open_bin(bin_id)
    # Then
    expect(bin_page.wait_until_live().label).to_have_text("opened by id")
    assert bin_page.bin_id == bin_id


def test_given_capture_url_when_user_opens_it_then_the_bin_page_shows(home: HomePage, api: StudioApi) -> None:
    """Given a bin's capture URL with a sub-path, when the user opens it from the home page, then the bin shows."""
    # Given
    bin_id = api.create_bin("opened by URL")
    home.goto()
    # When
    bin_page = home.open_bin(api.capture_url(bin_id, "/github?x=1"))
    # Then
    expect(bin_page.wait_until_live().label).to_have_text("opened by URL")
    assert bin_page.bin_id == bin_id


def test_given_text_without_a_bin_id_when_user_opens_it_then_a_warning_shows(home: HomePage) -> None:
    """Given text that holds no bin id, when the user opens it, then a warning shows and the page stays."""
    # Given
    home.goto()
    # When
    home.open_bin("not a bin")
    # Then
    expect(home.text("Type a bin id, or a URL that holds one.")).to_be_visible()
    expect(home.open_box).to_have_value("not a bin")


def test_given_browser_listing_when_user_makes_bin_and_reloads_home_then_bin_is_listed(home: HomePage) -> None:
    """Given `browser` listing, when the user makes a bin and reloads the home page, then the bin is still listed."""
    # Given
    home.goto().make_bin("kept in this browser")
    # When
    home.goto().reload()
    # Then
    expect(home.row("kept in this browser")).to_have_count(1)


def test_given_listed_bin_when_it_is_deleted_elsewhere_then_home_drops_it(home: HomePage, api: StudioApi) -> None:
    """Given a bin on the home page, when it is deleted through the API, then home drops it on its next load."""
    # Given
    bin_id = home.goto().make_bin("short-lived").bin_id
    home.goto()
    expect(home.row("short-lived")).to_have_count(1)
    # When
    api.delete_bin(bin_id)
    home.goto()
    # Then
    expect(home.row("short-lived")).to_have_count(0)
    expect(home.text("No bins yet.")).to_be_visible()


def test_given_new_bin_when_home_lists_it_then_it_expires_in_seven_days(home: HomePage) -> None:
    """Given a new bin, when the home page lists it, then its row says it expires in 7 days."""
    # Given
    home.goto().make_bin("expiry")
    # When
    home.goto()
    # Then
    expect(home.row("expiry")).to_contain_text("in 7 days")
