"""Load the tickets off disk.

Two small jobs: read the test set we grade on, and read the few-shot example
pool we show the model. Both are plain CSVs with columns id, text, label.

A `Ticket` is just an id + the text + the true label. We use a dataclass rather
than a bare tuple so the code that uses it reads in English (`ticket.text`, not
`ticket[1]`).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

# data/ sits next to this package's parent (the project root), so climb two
# levels: prompt_lab/ -> build_from_scratch/ -> and look for data/ there.
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


@dataclass(frozen=True)
class Ticket:
    """One support ticket: its id, the customer's words, and the true category."""

    id: int
    text: str
    label: str


def _read(path: Path) -> list[Ticket]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run `python generate_data.py` first to create it."
        )
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [Ticket(int(r["id"]), r["text"], r["label"]) for r in reader]


def load_tickets(data_dir: Path | None = None) -> list[Ticket]:
    """The 30-ticket test set we score every prompt style on."""
    return _read((data_dir or DATA_DIR) / "tickets.csv")


def load_fewshot_examples(data_dir: Path | None = None) -> list[Ticket]:
    """The 9 worked examples shown to the model in few-shot prompting.

    These are deliberately NOT in the test set -- showing the model an answer and
    then grading it on that same question would inflate the score dishonestly.
    """
    return _read((data_dir or DATA_DIR) / "fewshot_examples.csv")
