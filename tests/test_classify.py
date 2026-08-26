"""Tests for parsing model output and the offline classifier."""

from __future__ import annotations

from prompt_lab.classify import classify, parse_label


def test_parse_bare_word() -> None:
    assert parse_label("billing", "zero-shot").label == "billing"


def test_parse_word_inside_prose() -> None:
    # Free-form styles often wrap the answer in a sentence; we still find it.
    r = parse_label("This is clearly a technical problem.", "zero-shot")
    assert r.label == "technical"


def test_parse_chain_of_thought_final_line() -> None:
    raw = "It mentions a refund, so it's about money.\nFinal category: billing"
    assert parse_label(raw, "chain-of-thought").label == "billing"


def test_parse_structured_json() -> None:
    raw = '{"category": "other", "confidence": 0.7, "reason": "a feature request"}'
    r = parse_label(raw, "structured-json")
    assert r.label == "other"
    assert r.parsed_ok


def test_parse_unreadable_answer() -> None:
    # No category word anywhere -> we report failure rather than guessing.
    r = parse_label("I have no idea what this is about.", "zero-shot")
    assert r.label is None
    assert r.parsed_ok is False


def test_offline_classify_is_deterministic() -> None:
    a = classify("My card was charged twice this month.", "zero-shot")
    b = classify("My card was charged twice this month.", "zero-shot")
    assert a.label == b.label == "billing"
