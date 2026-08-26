"""Tests for loading the dataset."""

from __future__ import annotations

from prompt_lab import CATEGORIES
from prompt_lab.data import load_fewshot_examples, load_tickets


def test_test_set_has_thirty_tickets() -> None:
    tickets = load_tickets()
    assert len(tickets) == 30


def test_every_label_is_a_known_category() -> None:
    for ticket in load_tickets():
        assert ticket.label in CATEGORIES


def test_classes_are_balanced() -> None:
    counts = {c: 0 for c in CATEGORIES}
    for ticket in load_tickets():
        counts[ticket.label] += 1
    assert counts == {"billing": 10, "technical": 10, "other": 10}


def test_fewshot_pool_is_disjoint_from_test_set() -> None:
    # The whole point of a separate example pool: no leakage. If any example text
    # also appears in the test set, accuracy numbers would be dishonest.
    test_texts = {t.text for t in load_tickets()}
    example_texts = {e.text for e in load_fewshot_examples()}
    assert test_texts.isdisjoint(example_texts)
