# config.py — connection details for each jig, loaded from .env

import os
from dotenv import load_dotenv

load_dotenv()  # reads .env in the current working directory

def _require(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Missing required env var: {key} (check your .env file)")
    return value

JIGS = [
    {
        "id": "jig2",
        "name": "Jig 2",
        "host": _require("JIG2_HOST"),
        "user": _require("JIG2_USER"),
        "key_path": os.environ.get("JIG2_KEY_PATH") or None,
        "password": os.environ.get("JIG2_PASSWORD") or None,
        "port": int(os.environ.get("JIG2_PORT", 22)),
    },
    {
        "id": "jig3",
        "name": "Jig 3",
        "host": _require("JIG3_HOST"),
        "user": _require("JIG3_USER"),
        "key_path": os.environ.get("JIG3_KEY_PATH") or None,
        "password": os.environ.get("JIG3_PASSWORD") or None,
        "port": int(os.environ.get("JIG3_PORT", 22)),
    },
]