"""Score a prompt style against the labelled test set.

This is the "eval mindset" the project is really about. Building a classifier is
easy; *proving* one prompt is better than another needs a number you trust. Here
we compute three things per style:

  accuracy   the share of tickets it got exactly right (correct / total)
  parse rate the share of answers we could actually read a category out of
             (free-form styles can ramble; this is where structured JSON shines)
  confusion  which categories get mistaken for which -- the *shape* of the errors

Accuracy is one number; the confusion matrix tells you the story behind it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import CATEGORIES
from .classify import classify
from .data import Ticket, load_fewshot_examples


@dataclass
class StyleScore:
    """Everything we learned about one prompt style on the test set."""

    style: str
    total: int
    correct: int
    parsed_ok: int
    # confusion[true][predicted] = count
    confusion: dict[str, dict[str, int]] = field(default_factory=dict)
    errors: list[tuple[Ticket, str | None]] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def parse_rate(self) -> float:
        return self.parsed_ok / self.total if self.total else 0.0


def evaluate_style(
    style: str,
    tickets: list[Ticket],
    *,
    examples: list[Ticket] | None = None,
    offline: bool = True,
    model: str | None = None,
) -> StyleScore:
    """Run one style over every ticket and tally the results."""
    if style == "few-shot" and examples is None:
        examples = load_fewshot_examples()

    confusion = {t: {p: 0 for p in CATEGORIES} for t in CATEGORIES}
    correct = parsed_ok = 0
    errors: list[tuple[Ticket, str | None]] = []

    for ticket in tickets:
        result = classify(
            ticket.text, style, examples=examples, offline=offline, model=model
        )
        if result.parsed_ok:
            parsed_ok += 1
        # An unreadable answer counts as wrong but is left out of the confusion
        # matrix (we don't know which cell it belongs in).
        if result.label in CATEGORIES:
            confusion[ticket.label][result.label] += 1
        if result.label == ticket.label:
            correct += 1
        else:
            errors.append((ticket, result.label))

    return StyleScore(style, len(tickets), correct, parsed_ok, confusion, errors)


def compare_table(scores: list[StyleScore]) -> str:
    """A plain-text leaderboard, best accuracy first."""
    ordered = sorted(scores, key=lambda s: s.accuracy, reverse=True)
    lines = [
        f"{'style':<18}{'accuracy':>10}{'parsed':>10}",
        "-" * 38,
    ]
    for s in ordered:
        lines.append(
            f"{s.style:<18}{s.accuracy:>9.0%}{s.parse_rate:>10.0%}"
        )
    return "\n".join(lines)


def confusion_table(score: StyleScore) -> str:
    """Pretty-print one style's confusion matrix (rows = true, cols = predicted)."""
    cats = list(CATEGORIES)
    header = "true \\ pred   " + "".join(f"{c[:5]:>8}" for c in cats)
    lines = [f"[{score.style}]  accuracy {score.accuracy:.0%}", header]
    for t in cats:
        row = f"{t:<12}" + "".join(f"{score.confusion[t][p]:>8}" for p in cats)
        lines.append(row)
    return "\n".join(lines)
