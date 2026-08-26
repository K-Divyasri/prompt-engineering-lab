"""Tests for the pydantic validation schema."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from prompt_lab.schema import TicketLabel


def test_accepts_a_valid_object() -> None:
    label = TicketLabel.model_validate_json(
        '{"category": "billing", "confidence": 0.9, "reason": "about a charge"}'
    )
    assert label.category == "billing"
    assert label.confidence == 0.9


def test_category_and_optionals() -> None:
    # confidence and reason are optional.
    label = TicketLabel(category="technical")
    assert label.confidence is None


def test_rejects_unknown_category() -> None:
    with pytest.raises(ValidationError):
        TicketLabel(category="refunds")  # type: ignore[arg-type]


def test_rejects_out_of_range_confidence() -> None:
    with pytest.raises(ValidationError):
        TicketLabel(category="other", confidence=1.5)


def test_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TicketLabel.model_validate({"category": "other", "sentiment": "angry"})
