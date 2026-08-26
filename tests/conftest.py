"""Shared test fixtures.

Make sure the dataset exists before any test runs, so the suite passes on a
fresh checkout without the user having to remember to generate it first.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session", autouse=True)
def ensure_dataset() -> None:
    if not (ROOT / "data" / "tickets.csv").exists():
        subprocess.run([sys.executable, "generate_data.py"], cwd=ROOT, check=True)
