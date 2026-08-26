"""The five prompt styles, side by side.

This is the most important file in the project. Every function here takes the
text of one ticket and returns a list of chat *messages* -- the format every
modern LLM API expects:

    [{"role": "system", "content": "..."},
     {"role": "user",   "content": "..."}]

The `system` message sets the rules and persona; the `user` message carries the
actual request. Read the five builders back to back and you can see, in plain
text, exactly what makes each prompting technique different. That difference is
the whole subject of this project.

The five styles:

  1. zero-shot          Just ask. No examples. Relies on what the model already knows.
  2. few-shot           Show a handful of solved examples first, then ask.
  3. chain-of-thought   Ask it to reason step by step before committing to an answer.
  4. role-prompting     Give it a persona ("you are a senior support lead") to set tone
                        and raise care.
  5. structured-json    Force the answer into a strict JSON shape we can validate.

All five are aimed at the SAME task: read a ticket, return one of
billing / technical / other.
"""

from __future__ import annotations

from .data import Ticket

Message = dict[str, str]

# The task description, shared by the styles that don't need to phrase it specially.
_TASK = (
    "Classify the support ticket into exactly one of these categories:\n"
    "- billing: anything about money -- charges, refunds, invoices, plans, payment.\n"
    "- technical: something is broken -- errors, crashes, logins, bugs, sync issues.\n"
    "- other: everything else -- feature requests, praise, how-to and pricing questions."
)


def zero_shot(text: str) -> list[Message]:
    """Style 1 -- zero-shot. Direct instruction, no examples.

    The simplest prompt there is. We tell the model the task and the allowed
    answers and ask for one word back. It works well when the task is common and
    well understood (text classification is), and it's the baseline every other
    style has to beat.
    """
    system = (
        f"You are a support-ticket classifier. {_TASK}\n\n"
        "Answer with ONLY the single category word and nothing else."
    )
    user = f"Ticket: {text}\nCategory:"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def few_shot(text: str, examples: list[Ticket]) -> list[Message]:
    """Style 2 -- few-shot. Show solved examples, then ask.

    We paste a few already-labelled tickets into the prompt. The model isn't
    being retrained -- it's pattern-matching off the examples right there in the
    context ("in-context learning"). A handful of clear examples nudges it toward
    the exact format and the exact judgement calls you want. 3-5 is the usual
    sweet spot; we use a few per category.
    """
    system = (
        f"You are a support-ticket classifier. {_TASK}\n\n"
        "Here are some examples. Then classify the final ticket the same way.\n"
        "Answer with ONLY the single category word."
    )
    shots = "\n".join(f"Ticket: {ex.text}\nCategory: {ex.label}\n" for ex in examples)
    user = f"{shots}\nTicket: {text}\nCategory:"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def chain_of_thought(text: str) -> list[Message]:
    """Style 3 -- chain-of-thought. Reason first, answer last.

    Instead of demanding an instant answer, we invite the model to think out loud
    -- weigh what the ticket is really about -- and only then commit. For ambiguous
    tickets ("you charged me before I could cancel" -- billing or technical?) that
    short reasoning step often flips a wrong snap-judgement into a right one. The
    cost is more tokens and a longer answer we have to parse.
    """
    system = (
        f"You are a support-ticket classifier. {_TASK}\n\n"
        "Think it through in 1-2 short sentences, then end with a line in exactly "
        "this form:\nFinal category: <billing|technical|other>"
    )
    user = f"Ticket: {text}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def role_prompting(text: str) -> list[Message]:
    """Style 4 -- role prompting. Give the model a persona.

    We open by telling the model *who it is*: a seasoned support lead who has
    triaged thousands of tickets. A well-chosen role primes the tone and can lift
    care and accuracy on judgement-heavy tasks. The actual question is the same as
    zero-shot -- only the framing changed.
    """
    system = (
        "You are a senior customer-support lead with ten years of experience. You "
        "have triaged tens of thousands of tickets and you route each one to the "
        f"right team without fuss.\n\n{_TASK}\n\n"
        "Answer with ONLY the single category word."
    )
    user = f"Ticket: {text}\nCategory:"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def structured_json(text: str) -> list[Message]:
    """Style 5 -- structured output. Force a strict JSON shape.

    Here we don't want a word in prose -- we want machine-readable JSON we can
    validate and store. We describe the exact object we expect and tell the model
    to return that and nothing else. Paired with pydantic (see schema.py), this is
    how you make an LLM behave like a reliable function. Its big win is usually
    *reliability of parsing*, not raw accuracy.
    """
    system = (
        f"You are a support-ticket classifier. {_TASK}\n\n"
        "Respond with a single JSON object and no other text, in exactly this form:\n"
        '{"category": "billing|technical|other", "confidence": 0.0-1.0, '
        '"reason": "<one short sentence>"}'
    )
    user = f"Ticket: {text}"
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


# A registry so the CLI and the evaluator can look a style up by name.
STYLES = {
    "zero-shot": zero_shot,
    "few-shot": few_shot,
    "chain-of-thought": chain_of_thought,
    "role": role_prompting,
    "structured-json": structured_json,
}


def build_messages(style: str, text: str, examples: list[Ticket] | None = None) -> list[Message]:
    """Build the messages for `style`. few-shot is the only one needing examples."""
    if style not in STYLES:
        raise ValueError(f"Unknown style {style!r}. Choose from {list(STYLES)}.")
    if style == "few-shot":
        if not examples:
            raise ValueError("few-shot needs a non-empty list of examples.")
        return few_shot(text, examples)
    return STYLES[style](text)  # type: ignore[operator]
