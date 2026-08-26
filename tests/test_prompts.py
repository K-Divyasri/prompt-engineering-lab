"""Tests for the five prompt builders."""

from __future__ import annotations

import pytest

from prompt_lab.data import Ticket
from prompt_lab.prompts import STYLES, build_messages

EXAMPLES = [
    Ticket(1, "My card was charged twice.", "billing"),
    Ticket(2, "The app crashes on export.", "technical"),
    Ticket(3, "Please add a dark mode.", "other"),
]


def test_all_five_styles_registered() -> None:
    assert set(STYLES) == {
        "zero-shot", "few-shot", "chain-of-thought", "role", "structured-json"
    }


@pytest.mark.parametrize("style", ["zero-shot", "chain-of-thought", "role", "structured-json"])
def test_styles_produce_system_and_user_messages(style: str) -> None:
    messages = build_messages(style, "I was double charged this month.")
    roles = [m["role"] for m in messages]
    assert roles == ["system", "user"]
    # The ticket text must reach the model.
    assert "double charged" in messages[-1]["content"]


def test_few_shot_includes_the_examples() -> None:
    messages = build_messages("few-shot", "New ticket here.", examples=EXAMPLES)
    blob = " ".join(m["content"] for m in messages)
    for ex in EXAMPLES:
        assert ex.text in blob
        assert ex.label in blob


def test_few_shot_requires_examples() -> None:
    with pytest.raises(ValueError):
        build_messages("few-shot", "x", examples=[])


def test_structured_style_asks_for_json() -> None:
    messages = build_messages("structured-json", "x")
    assert "JSON" in messages[0]["content"] or "json" in messages[0]["content"]


def test_unknown_style_raises() -> None:
    with pytest.raises(ValueError):
        build_messages("telepathy", "x")
