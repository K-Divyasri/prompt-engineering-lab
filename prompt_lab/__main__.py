"""Lets you run the package as `python -m prompt_lab`."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
