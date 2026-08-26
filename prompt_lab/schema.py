"""The shape a *structured* answer must take, enforced by pydantic.

When we ask the model for JSON (the fifth prompt style), we don't want to just
hope it comes back well-formed. We define exactly what a valid answer looks like
-- a `category` that is one of our three labels, an optional confidence between 0
and 1, and an optional one-line reason -- and let pydantic check it for us.

If the model returns `{"category": "techncial"}` (a typo) or invents a fourth
category, pydantic raises a `ValidationError` instead of letting the bad value
flow downstream. That is the whole point of validation: fail loudly and early.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

# Literal pins the field to exactly these three strings. Anything else fails
# validation -- this is how we stop the model from inventing new categories.
Category = Literal["billing", "technical", "other"]


class TicketLabel(BaseModel):
    """A validated classification of one ticket."""

    category: Category
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="How sure the model is, 0 to 1. Optional.",
    )
    reason: Optional[str] = Field(
        default=None,
        description="A short justification. Optional.",
    )

    # Reject any extra keys the model tacks on, so the schema stays tight.
    model_config = {"extra": "forbid"}
