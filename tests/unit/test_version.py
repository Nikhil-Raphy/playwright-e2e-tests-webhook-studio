"""Tests for the package version."""

from importlib.metadata import version

import webhook_studio_e2e
from webhook_studio_e2e import _version


def test_given_version_file_when_package_is_installed_then_metadata_and_package_match_it() -> None:
    """Given the version in _version.py, when the package is installed, then its metadata and __version__ match it."""
    # Given
    expected = _version.__version__
    # When
    installed = version("playwright-e2e-tests-webhook-studio")
    # Then
    assert (installed, webhook_studio_e2e.__version__) == (expected, expected)
