"""Create the support-ticket dataset this whole project runs on.

Run it once, from the project root:

    python generate_data.py

It writes two files into data/:

  - tickets.csv          30 labelled tickets. This is the TEST SET. Every prompt
                         style is scored on these, and on these only.
  - fewshot_examples.csv  9 labelled tickets used as the examples we *show* the
                         model in few-shot prompting. They are kept completely
                         separate from the test set on purpose (see below).

WHY TWO FILES?
  In few-shot prompting you hand the model a few solved examples before asking it
  to solve a new one. If those examples were also in your test set, the model would
  be "seeing the answers" to questions you then grade it on -- that's cheating, and
  it makes your accuracy number a lie. Keeping the example pool and the test set
  disjoint is the single most important habit in evaluation. We bake it in here so
  you build the right instinct from day one.

THE TASK:
  Classify each ticket into exactly one of three categories:
    billing    -- money: charges, refunds, invoices, plans, payment methods.
    technical  -- it's broken: errors, crashes, logins, bugs, things not working.
    other      -- everything else: feature requests, praise, how-do-I questions.

The data is hand-written and fixed (no randomness), so everyone who runs this gets
the byte-for-byte same files and the same scores. That reproducibility is what lets
you compare prompt styles fairly.
"""

from __future__ import annotations

import csv
from pathlib import Path

# --- The example pool (shown to the model in few-shot prompting) ----------------
# Three per category. Short, clear, unambiguous -- good examples teach a pattern,
# they don't show off edge cases.
FEWSHOT: list[tuple[str, str]] = [
    ("My card was charged twice for the same monthly subscription.", "billing"),
    ("Can I get an invoice with my company's VAT number on it?", "billing"),
    ("I want to downgrade from the Pro plan to the free tier.", "billing"),
    ("The app crashes every time I tap the export button.", "technical"),
    ("I can't log in -- it says my password is wrong but it isn't.", "technical"),
    ("The dashboard shows a 500 error and won't load any charts.", "technical"),
    ("Do you have a dark mode? I'd love one for night shifts.", "other"),
    ("Just wanted to say your support team was incredibly helpful!", "other"),
    ("Is there a keyboard shortcut to start a new project?", "other"),
]

# --- The test set (what every prompt style is graded on) ------------------------
# 30 tickets, 10 per category. A few are deliberately a little tricky -- that's
# where prompt style starts to matter, which is the whole point of the project.
TEST: list[tuple[str, str]] = [
    # billing (10)
    ("I was billed $49 but my plan is supposed to be $29 a month.", "billing"),
    ("Please cancel my subscription and refund the last payment.", "billing"),
    ("My credit card expired -- how do I update my payment method?", "billing"),
    ("Why is there a tax charge on my invoice that wasn't there last month?", "billing"),
    ("I upgraded to annual billing but I'm still being charged monthly.", "billing"),
    ("Can you send me a receipt for the payment I made in March?", "billing"),
    ("I was promised a discount code but the full price was charged.", "billing"),
    ("The free trial ended and you charged me before I could cancel.", "billing"),
    ("Do you offer student pricing, and how would I get the lower rate?", "billing"),
    ("There are two charges on my statement from your company today.", "billing"),
    # technical (10)
    ("The website is completely down for me, just a blank white page.", "technical"),
    ("Every time I upload a file the page freezes and I lose my work.", "technical"),
    ("I keep getting 'invalid token' errors when calling your API.", "technical"),
    ("The mobile app won't sync and shows data from three days ago.", "technical"),
    ("After the latest update my saved settings all disappeared.", "technical"),
    ("Two-factor codes never arrive so I'm locked out of my account.", "technical"),
    ("Charts render as broken images in Safari but work in Chrome.", "technical"),
    ("The search box returns no results even for things I know exist.", "technical"),
    ("Exporting to PDF produces a corrupted file that won't open.", "technical"),
    ("Notifications stopped working entirely after I reinstalled the app.", "technical"),
    # other (10)
    ("Could you add support for exporting to Excel in a future release?", "other"),
    ("What's the difference between the Team and Enterprise plans?", "other"),
    ("I'd like to request an integration with Google Calendar.", "other"),
    ("Your new design looks fantastic -- great work to the team!", "other"),
    ("Is there documentation on how to organise projects into folders?", "other"),
    ("Do you have an affiliate or referral program I could join?", "other"),
    ("Can I use your product for a non-profit, and are there guidelines?", "other"),
    ("Where can I find tutorials for getting started as a new user?", "other"),
    ("Will there be a mobile version for tablets at some point?", "other"),
    ("How do I invite a teammate to collaborate on my workspace?", "other"),
]


def _write(path: Path, rows: list[tuple[str, str]], start_id: int = 1) -> None:
    """Write rows as a CSV with columns id, text, label."""
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "text", "label"])
        for i, (text, label) in enumerate(rows, start=start_id):
            writer.writerow([i, text, label])


def main() -> None:
    data_dir = Path(__file__).resolve().parent / "data"
    data_dir.mkdir(exist_ok=True)

    _write(data_dir / "tickets.csv", TEST)
    _write(data_dir / "fewshot_examples.csv", FEWSHOT)

    print(f"Wrote {len(TEST)} test tickets   -> {data_dir / 'tickets.csv'}")
    print(f"Wrote {len(FEWSHOT)} few-shot examples -> {data_dir / 'fewshot_examples.csv'}")
    print("\nCategory counts in the test set:")
    counts: dict[str, int] = {}
    for _, label in TEST:
        counts[label] = counts.get(label, 0) + 1
    for label in ("billing", "technical", "other"):
        print(f"  {label:10s} {counts[label]}")


if __name__ == "__main__":
    main()
