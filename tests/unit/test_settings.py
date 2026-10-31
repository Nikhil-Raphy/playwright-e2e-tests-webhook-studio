"""Tests for reading the settings from environment variables."""

import pytest

from webhook_studio_e2e.settings import DEFAULT_BASE_URL, Settings, SettingsError


def test_given_no_variables_when_settings_load_then_only_the_default_app_is_set() -> None:
    """Given no variables, when the settings load, then the app is on localhost:17300 with no local-mode app."""
    # Given
    environ: dict[str, str] = {}
    # When
    settings = Settings.from_env(environ)
    # Then
    assert settings == Settings(base_url=DEFAULT_BASE_URL, local_replay_url=None, echo_url=None)


def test_given_every_variable_when_settings_load_then_each_url_is_kept_without_its_last_slash() -> None:
    """Given all three variables, when the settings load, then each URL is kept and loses any trailing slash."""
    # Given
    environ = {
        "E2E_BASE_URL": " http://app:17300/ ",
        "E2E_LOCAL_REPLAY_URL": "http://app-local:17300",
        "E2E_ECHO_URL": "http://echo:8080/",
    }
    # When
    settings = Settings.from_env(environ)
    # Then
    assert settings == Settings("http://app:17300", "http://app-local:17300", "http://echo:8080")


@pytest.mark.parametrize("value", ["ftp://app", "app:17300", "http://", "http://app/?x=1", "http://app/#top"])
def test_given_bad_url_when_settings_load_then_the_error_names_the_variable(value: str) -> None:
    """Given a value that is not a plain http or https URL, when the settings load, then the error names it."""
    # Given
    environ = {"E2E_ECHO_URL": value}
    # When
    with pytest.raises(SettingsError) as raised:
        Settings.from_env(environ)
    # Then
    assert "E2E_ECHO_URL" in str(raised.value)
