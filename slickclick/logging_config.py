"""Application-wide logging setup.

Writes to %APPDATA%/SlickClick/slickclick.log so errors are
visible even when the app is packaged as a windowless exe.
"""

import logging
import os

_LOG_DIR = os.path.join(os.environ.get("APPDATA", "."), "SlickClick")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOG_DIR, "slickclick.log")

logger = logging.getLogger("slickclick")
logger.setLevel(logging.DEBUG)

# File handler — rotates implicitly by overwriting each launch
_fh = logging.FileHandler(_LOG_FILE, mode="w", encoding="utf-8")
_fh.setLevel(logging.DEBUG)
_fh.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
))
logger.addHandler(_fh)
