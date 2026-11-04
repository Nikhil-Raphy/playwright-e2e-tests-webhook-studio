"""Where the apps under test and the echo service live, read once from environment variables."""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

if TYPE_CHECKING:
    from collections.abc import Mapping

DEFAULT_BASE_URL = "http://localhost:17300"


class SettingsError(ValueError):
    """An environment variable holds a value the tests cannot use."""


@dataclass(frozen=True, slots=True)
class Settings:
    """Where the tests find the apps they drive.

    Attributes:
        base_url: The app in its default `restricted` replay mode.
        local_replay_url: The app in `local` replay mode, or None when there is none.
        echo_url: The echo service, as the local-mode app reaches it, or None when there is none.
    """

    base_url: str = DEFAULT_BASE_URL
    local_replay_url: str | None = None
    echo_url: str | None = None

    @classmethod
    def from_env(cls, environ: Mapping[str, str] = os.environ) -> Settings:
        """Read the settings from environment variables.

        Args:
            environ: The variables to read: `E2E_BASE_URL`, `E2E_LOCAL_REPLAY_URL` and `E2E_ECHO_URL`.

        Returns:
            The settings.
        """
        return cls(
            base_url=_url(environ, "E2E_BASE_URL") or DEFAULT_BASE_URL,
            local_replay_url=_url(environ, "E2E_LOCAL_REPLAY_URL"),
            echo_url=_url(environ, "E2E_ECHO_URL"),
        )


def _url(environ: Mapping[str, str], name: str) -> str | None:
    """Read one URL variable: None when unset or blank, else the URL without a trailing slash."""
    raw = environ.get(name, "").strip()
    if not raw:
        return None
    parts = urlsplit(raw)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.query or parts.fragment:
        msg = f"{name} must be an http or https URL with a host and no query, such as http://localhost:17300."
        raise SettingsError(msg)
    return raw.rstrip("/")
