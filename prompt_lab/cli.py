"""The `prompt-lab` command line tool.

Examples (run from the repo root):

    python -m prompt_lab                      # score all five styles, offline
    python -m prompt_lab --style few-shot     # just one style
    python -m prompt_lab --confusion          # also print confusion matrices
    python -m prompt_lab --errors             # list the tickets each style missed
    python -m prompt_lab --real               # use a REAL model (needs an API key)

Offline is the default so it works on any machine with no key. Add --real once
you've put a key in a .env file (see .env.example) to get real model numbers.
"""

from __future__ import annotations

import argparse

from .data import load_fewshot_examples, load_tickets
from .evaluate import compare_table, confusion_table, evaluate_style
from .prompts import STYLES


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prompt-lab",
        description="Compare five prompt styles on support-ticket classification.",
    )
    p.add_argument(
        "--style",
        choices=[*STYLES.keys(), "all"],
        default="all",
        help="Which prompt style to score (default: all).",
    )
    p.add_argument(
        "--real",
        action="store_true",
        help="Call a real model via LiteLLM (needs an API key). Default is offline.",
    )
    p.add_argument(
        "--model",
        default=None,
        help="Model name for --real, e.g. gemini/gemini-1.5-flash (LiteLLM format).",
    )
    p.add_argument("--confusion", action="store_true", help="Print confusion matrices.")
    p.add_argument("--errors", action="store_true", help="List missed tickets per style.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    offline = not args.real

    tickets = load_tickets()
    examples = load_fewshot_examples()
    styles = list(STYLES.keys()) if args.style == "all" else [args.style]

    mode = "OFFLINE (fake model -- no API key used)" if offline else f"REAL ({args.model or 'default'})"
    print(f"Scoring on {len(tickets)} tickets. Mode: {mode}\n")

    scores = [
        evaluate_style(s, tickets, examples=examples, offline=offline, model=args.model)
        for s in styles
    ]

    print(compare_table(scores))

    if args.confusion:
        print()
        for s in scores:
            print()
            print(confusion_table(s))

    if args.errors:
        for s in scores:
            print(f"\n[{s.style}] missed {len(s.errors)} ticket(s):")
            for ticket, got in s.errors:
                print(f"  true={ticket.label:9s} got={got!s:9s} :: {ticket.text}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
