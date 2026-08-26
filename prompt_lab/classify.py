"""Send a ticket to a model and read back a single category.

Two modes, one interface:

  REAL mode    Calls a real LLM through LiteLLM (one function, many providers).
               Needs an API key in your environment. This is what you ship.

  OFFLINE mode A small deterministic stand-in -- a "fake model" -- that needs no
               key, no network, and no money. It lets the whole project run, and
               every notebook and test pass, on a fresh laptop. It is NOT a real
               language model: it's keyword rules with a few documented tweaks per
               prompt style, just enough to make the comparison table meaningful.
               When you add a real key, flip offline off and you get real numbers.

Whichever mode produced the raw text, the SAME parser turns it into a label, so
the rest of the program never has to care where the answer came from.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass

from . import CATEGORIES
from .data import Ticket
from .prompts import build_messages
from .schema import TicketLabel


@dataclass
class Result:
    """The outcome of classifying one ticket."""

    label: str | None  # the parsed category, or None if we couldn't read one
    raw: str  # exactly what the model returned, for debugging
    parsed_ok: bool  # did we successfully extract a valid category?


# --------------------------------------------------------------------------- #
#  Parsing: raw model text -> a clean category label                          #
# --------------------------------------------------------------------------- #
def _first_category_word(text: str) -> str | None:
    """Return the first of our three category words found in `text`, else None."""
    low = text.lower()
    hits = [(low.find(c), c) for c in CATEGORIES if c in low]
    if not hits:
        return None
    return min(hits)[1]  # the one that appears earliest


def parse_label(raw: str, style: str) -> Result:
    """Pull a category out of the raw response, using rules suited to the style."""
    if style == "structured-json":
        # Find the JSON object and validate it against our pydantic schema.
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                obj = TicketLabel.model_validate_json(match.group(0))
                return Result(obj.category, raw, True)
            except Exception:
                pass  # fall through to the loose parser below
    if style == "chain-of-thought":
        # Prefer the explicit "Final category: X" line if present.
        m = re.search(r"final category\s*:\s*([a-z]+)", raw, re.IGNORECASE)
        if m and m.group(1).lower() in CATEGORIES:
            return Result(m.group(1).lower(), raw, True)
    # Default: the first category word anywhere in the text.
    label = _first_category_word(raw)
    return Result(label, raw, label is not None)


# --------------------------------------------------------------------------- #
#  Offline "fake model"                                                       #
# --------------------------------------------------------------------------- #
# Keyword rules. Each list votes for its category; the category with the most
# hits wins. These are intentionally simple -- a real model is far smarter -- but
# they give us a believable baseline with believable mistakes.
_KEYWORDS: dict[str, list[str]] = {
    "billing": [
        "charge", "charged", "bill", "billed", "refund", "invoice", "payment",
        "subscription", "price", "card", "receipt", "tax", "plan", "$",
    ],
    "technical": [
        "error", "crash", "broken", "freeze", "frozen", "login", "log in",
        "password", "bug", "sync", "500", "blank", "token", "render", "corrupt",
        "upload",
    ],
    "other": [
        "feature", "integration", "documentation", "tutorial", "referral",
        "affiliate", "invite", "dark mode", "shortcut", "difference between",
    ],
}


def _keyword_guess(text: str) -> str:
    low = text.lower()
    scores = {cat: sum(low.count(kw) for kw in kws) for cat, kws in _KEYWORDS.items()}
    best = max(scores.values())
    if best == 0:
        return "other"  # nothing matched -- default bucket
    # Tie-break in a fixed order so results are deterministic.
    for cat in ("technical", "billing", "other"):
        if scores[cat] == best:
            return cat
    return "other"


# SIMULATED per-style improvements. These say: "with this better prompt, the model
# would get these specific tricky tickets right that the plain keyword baseline
# misses." They are matched on a distinctive snippet of the ticket text. This is
# the one place we fake the *lesson* (better prompts -> better accuracy) so the
# offline comparison table isn't flat. With a real API key none of this runs.
_FIXES: dict[str, dict[str, str]] = {
    # Few-shot examples teach the model what "technical" looks like even when no
    # obvious keyword (error/crash/bug) is present -- a lockout, missing results,
    # notifications dying. So few-shot recovers those implicit-technical tickets.
    "few-shot": {
        "saved settings all disappeared": "technical",
        "locked out": "technical",
        "returns no results": "technical",
        "stopped working": "technical",
    },
    # Reasoning step by step lets it untangle the trickiest ones: that "plans" in
    # a pricing comparison is a how-it-works question (other), and that "student
    # pricing" is about money (billing) -- plus the implicit-technical cases.
    "chain-of-thought": {
        "locked out": "technical",
        "returns no results": "technical",
        "stopped working": "technical",
        "student pricing": "billing",
        "difference between the team": "other",
    },
    # A persona nudges care a little, but not as much as examples or reasoning.
    "role": {
        "locked out": "technical",
    },
}


def _apply_fixes(text: str, base: str, style: str) -> str:
    low = text.lower()
    for snippet, corrected in _FIXES.get(style, {}).items():
        if snippet in low:
            return corrected
    return base


def fake_complete(text: str, style: str) -> str:
    """Produce raw text in the FORMAT the given style would elicit from a real model.

    The format matters: it means the real parser above is genuinely exercised
    offline -- JSON for the structured style, a reasoning line for chain-of-thought,
    a bare word otherwise.
    """
    label = _apply_fixes(text, _keyword_guess(text), style)
    if style == "structured-json":
        return json.dumps({"category": label, "confidence": 0.8,
                           "reason": "matched the category's typical wording."})
    if style == "chain-of-thought":
        return (f"The ticket is mainly about this topic, which points to {label}.\n"
                f"Final category: {label}")
    return label


# --------------------------------------------------------------------------- #
#  Real model call (LiteLLM)                                                  #
# --------------------------------------------------------------------------- #
DEFAULT_MODEL = os.environ.get("PLAB_MODEL", "gemini/gemini-1.5-flash")


def real_complete(messages: list[dict[str, str]], model: str) -> str:
    """Call a real model via LiteLLM. Imported lazily so offline mode needs no install."""
    from litellm import completion  # noqa: PLC0415  (lazy on purpose)

    response = completion(model=model, messages=messages, temperature=0)
    return response.choices[0].message.content or ""


# --------------------------------------------------------------------------- #
#  The one function the rest of the program calls                             #
# --------------------------------------------------------------------------- #
def classify(
    text: str,
    style: str,
    *,
    examples: list[Ticket] | None = None,
    offline: bool = True,
    model: str | None = None,
) -> Result:
    """Classify one ticket with one prompt style. Returns a `Result`.

    offline=True (the default) uses the fake model -- no key needed. Set
    offline=False to call a real model through LiteLLM.
    """
    if offline:
        raw = fake_complete(text, style)
    else:
        messages = build_messages(style, text, examples)
        raw = real_complete(messages, model or DEFAULT_MODEL)
    return parse_label(raw, style)
