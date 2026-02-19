"""Check for updates via the GitHub Releases API."""

import threading
import urllib.request
import json

from .constants import APP_VERSION
from .logging_config import logger

_GITHUB_API = "https://api.github.com/repos/GoblinRules/SlickClick/releases/latest"


def _parse_version(tag: str) -> tuple[int, ...]:
    """Convert a version tag like 'V1.2.0' or 'v1.2.0' to a tuple of ints."""
    cleaned = tag.lstrip("vV").strip()
    try:
        return tuple(int(p) for p in cleaned.split("."))
    except ValueError:
        return (0,)


def check_for_updates(callback):
    """Check GitHub for updates in a background thread.

    Calls ``callback(result)`` on completion where *result* is a dict:
      - ``{"up_to_date": True}``
      - ``{"up_to_date": False, "latest": "1.3.0", "url": "https://..."}``
      - ``{"error": "message"}``
    """

    def _worker():
        try:
            req = urllib.request.Request(
                _GITHUB_API,
                headers={"Accept": "application/vnd.github.v3+json",
                          "User-Agent": "SlickClick-UpdateChecker"},
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            tag = data.get("tag_name", "")
            latest = _parse_version(tag)
            current = _parse_version(APP_VERSION)
            html_url = data.get("html_url", "")

            if latest > current:
                # Strip the leading v/V for display
                display = tag.lstrip("vV")
                logger.info("Update available: %s → %s", APP_VERSION, display)
                callback({"up_to_date": False, "latest": display, "url": html_url})
            else:
                logger.info("Up to date (current=%s, remote=%s)", APP_VERSION, tag)
                callback({"up_to_date": True})

        except Exception as e:
            logger.error("Update check failed: %s", e)
            callback({"error": str(e)})

    threading.Thread(target=_worker, daemon=True).start()
