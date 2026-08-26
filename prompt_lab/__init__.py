"""prompt_lab -- compare five prompt styles on a ticket-classification task.

The package is small and split by job so each piece is easy to read and test:

    data.py      load the tickets and the few-shot example pool
    schema.py    the pydantic model that validates a structured (JSON) answer
    prompts.py   build the messages for each of the five prompt styles
    classify.py  send a ticket to a model (or the offline fake one) and read the label
    evaluate.py  run a style over the whole test set and score it
    cli.py       the `prompt-lab` command that ties it together

The three categories never change, so they live here.
"""

from __future__ import annotations

CATEGORIES: tuple[str, str, str] = ("billing", "technical", "other")

__all__ = ["CATEGORIES"]
