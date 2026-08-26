# Prompt Engineering Lab

The Prompt Engineering Lab assembled the way a real repo is: small modules that
each do one job, a proper command-line tool, and a passing test suite.

**What it does:** runs the same task, classifying a support ticket as
`billing` / `technical` / `other`, across five prompt styles (zero-shot, few-shot,
chain-of-thought, role-prompting, and forced-JSON structured output), scores each on
a 30-ticket labelled test set, and prints a leaderboard plus confusion matrices so
you can see *which prompt wins and why*.

**It runs offline by default.** With no API key, a small deterministic "fake model"
stands in for a real LLM so the whole thing runs on any laptop, every command, every
test. When you add a free API key you flip one flag (`--real`) and get real numbers.

## Run it

```powershell
python -m venv .venv ; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python generate_data.py           # writes data/tickets.csv + fewshot_examples.csv
python -m prompt_lab               # score all five styles, offline
python -m prompt_lab --confusion   # add the confusion matrices
python -m prompt_lab --errors      # list the tickets each style missed
pytest                             # 27 tests
```

Offline, the leaderboard comes out like this (it's deterministic, so you'll see the
same numbers):

```
style               accuracy    parsed
--------------------------------------
chain-of-thought        97%      100%
few-shot                93%      100%
role                    83%      100%
zero-shot               80%      100%
structured-json         80%      100%
```

Read that as the project's headline lesson: **showing examples (few-shot) and asking
for reasoning (chain-of-thought) beat just asking (zero-shot); a persona (role) helps
a little; and structured JSON doesn't necessarily raise accuracy: its win is that
every answer parses cleanly, every time.** (See the note on the fake model below for
why these specific offline numbers exist.)

## Use a real model

```powershell
copy .env.example .env             # then paste in a free Gemini key
pip install -e ".[real]"
python -m prompt_lab --real                              # default model
python -m prompt_lab --real --model groq/llama-3.1-8b-instant --confusion
```

With a real model the numbers become real: the fake-model tweaks don't run at all.
Comparing the offline story to what a real model actually does is the most instructive
thing you can do here.

## How it's laid out

```
prompt-engineering-lab/
├── prompt_lab/
│   ├── __init__.py     the three category labels live here
│   ├── data.py         load the tickets + the few-shot example pool (a Ticket dataclass)
│   ├── schema.py       the pydantic model that validates a structured JSON answer
│   ├── prompts.py      the five prompt builders, the heart of the project
│   ├── classify.py     send a ticket to a model (or the offline fake), read back a label
│   ├── evaluate.py     score a style: accuracy, parse rate, confusion matrix
│   ├── cli.py          the `prompt-lab` command
│   └── __main__.py     lets you run `python -m prompt_lab`
├── tests/              27 pytest tests: data, prompts, schema, parsing, scoring
├── data/               the generated CSVs (git-ignored; regenerate any time)
├── generate_data.py    writes the dataset
├── pyproject.toml      packaging + pytest config
├── requirements.txt
└── .env.example        copy to .env for a real API key
```

## About the offline "fake model"

`classify.py` has a small keyword-based stand-in so nobody needs a paid key to learn
from this project. It is **not** a language model. To make the offline comparison table
teach the right lesson, it applies a few clearly-labelled, per-style corrections (few-shot
and chain-of-thought "recover" specific tricky tickets that the bare keyword baseline
misses). That is the *one* place the project simulates a result rather than measuring it,
and it's commented as such in the code. Every other moving part, the prompts, the JSON
parsing, the pydantic validation, the accuracy and confusion-matrix maths, is the real
thing, and behaves identically whether the text came from the fake model or a real one.

## What I learned

- The five core prompt patterns and, concretely, when each one earns its keep.
- Why you keep few-shot examples out of your test set, and what leakage does to a score.
- Forcing and validating structured JSON output with pydantic.
- Building an eval: accuracy, parse rate, and a confusion matrix that shows the *shape*
  of the mistakes, the beginning of the "measure before you ship" mindset.
