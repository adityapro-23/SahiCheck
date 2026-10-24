"""checks_registry.py – Loads the 16 ordered checks from data/rules.json.

Exposes one function `get_checks()` that returns a plain list of dicts so
`GET /api/checks` can reply instantly without running the pipeline.
The same order is used by pipeline.py when emitting streaming events.
"""

import json
import os
from typing import Any, Dict, List

_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
_CHECKS: List[Dict[str, Any]] = []  # cached after first load


def get_checks() -> List[Dict[str, Any]]:
    """Returns the 16 checks in order. Loads once, then uses the cached list."""
    global _CHECKS
    if not _CHECKS:
        path = os.path.join(_DATA_DIR, "rules.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Each entry: id, name, tier, source, max_points
        _CHECKS = data["checks"]
    return _CHECKS
