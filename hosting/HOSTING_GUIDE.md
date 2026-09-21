# Publishing Prompt Engineering Lab

This project isn't a website and it isn't a server. It's a command-line tool that runs on
your laptop, scores five prompt styles on a support-ticket classification task, and prints a
leaderboard plus confusion matrices. There's nothing to "deploy" in the usual sense — no box
to keep running, no port to expose.

So "hosting" here means something slightly different, and honestly more useful for someone
trying to get hired: turn the folder you built into a **GitHub repo a recruiter can open and
immediately get**. A clean README with the results table right there, a little green checkmark
that proves the tests pass on every push, and — optionally — a tiny live web demo anyone can
click. That checkmark is CI (Continuous Integration), and GitHub runs it for free.

Here's the whole plan, so you know where this is going:

1. **A GitHub repo** — your code, online, public, with a README that lands the project fast.
2. **CI** — GitHub automatically runs your 27 tests on every push. Green check = it works.
3. **(Optional) a live demo** — a small Streamlit app that shows the leaderboard in a browser,
   hosted free on Hugging Face Spaces or Streamlit Community Cloud.

The real code lives at the repo root: `prompt_lab/`, `tests/`, `generate_data.py`, and
`requirements.txt` sit directly next to this `hosting/` folder, so no path below needs a
subfolder prefix.

A note on the command: this guide uses `python -m prompt_lab ...`, because that's how the
package runs. After a `pip install -e .` you can also type `prompt-lab ...` directly. Both do
the same thing. Use whichever you actually installed.

---

## Step 0 — Install Git and make a GitHub account

Git is the program that tracks versions of your files. GitHub is the website that stores a
copy online so other people (and recruiters) can see it. You need both. They're different
things — Git runs on your laptop, GitHub lives on the internet. Git is the filing system;
GitHub is the shelf you put the folder on so others can reach it.

### Install Git

1. Go to https://git-scm.com/download/win. The download starts on its own.
2. Run the installer. Click Next through every screen — the defaults are fine. You do not
   need to understand any of the options.
3. When it finishes, open a **new** PowerShell window (it has to be new so it picks up the
   install) and check it worked:

```powershell
git --version
```

If you see something like `git version 2.45.0`, you're done. If PowerShell says it doesn't
recognize `git`, close every terminal, open a fresh one, and try again.

### Make a GitHub account

1. Go to https://github.com and sign up. Use your real email (`mathuransada@gmail.com` is the
   one on file). Verify it.
2. Pick a username you'd be happy putting on a CV — recruiters see it. `divya-dev` beats
   `xX_coder_Xx_2009`.
3. That's all for now. You'll make the actual repo in Step 3.

### Tell Git who you are

Do this once per machine. Git stamps your name and email onto every commit (a commit is a
saved snapshot of your code). Use the same email as your GitHub account.

```powershell
git config --global user.name "Your Name"
git config --global user.email "mathuransada@gmail.com"
```

---

## Step 1 — Know what goes in the repo and what must NOT

This is the part that bites people, so read it before you touch any Git command.

Some files belong on GitHub. Some must never leave your laptop. The line between them is a
file called `.gitignore` — a plain-text list of things Git pretends don't exist. The project
already ships one at the repo root (`.gitignore`). Open it and confirm it has at least
these lines:

```
.env
__pycache__/
*.pyc
.venv/
venv/
*.egg-info/
.pytest_cache/
data/*.csv
```

Here's what each one keeps out and why it matters:

- **`.env`** — this is the important one. If you use the `--real` flag, your `.env` holds an
  API key (your free Gemini key, or a Groq/Anthropic one). **A key is a password.** If you
  commit it, it's on the public internet **forever** — deleting it in a later commit doesn't
  help, because Git keeps the whole history, and bots scrape GitHub for leaked keys within
  minutes of a push. Someone else then runs up a bill on your account. So: **`.env` never gets
  committed, ever.** The repo ships a `.env.example` instead, which lists the variable names
  with blank values so other people know what to fill in. That one is safe and is *meant* to
  be committed. This is the golden rule of this whole guide — everything else is mechanics.
- **`data/*.csv`** — the tickets and few-shot examples are *generated* by `generate_data.py`,
  not hand-written source. Anyone who clones the repo just runs that script to recreate them,
  so there's no need to store them in Git. (One exception comes up later: if you deploy the
  live demo, you'll want the data available there — more on that in the demo section.)
- **`__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`** — junk Python and pytest
  create as they run. Nobody needs to see it; it just clutters the repo.
- **`.venv/`, `venv/`** — your virtual environment. It's hundreds of megabytes of installed
  packages specific to your machine. Other people rebuild it from `requirements.txt`; they
  never want yours.

The `.env.example` pattern, spelled out, because it's the safe habit to internalize:

```
# .env.example  -- committed. Names only, no values. Safe.
GEMINI_API_KEY=
PLAB_MODEL=gemini/gemini-1.5-flash
```

```
# .env  -- NEVER committed. Real secret. Git-ignored.
GEMINI_API_KEY=AIzaSyD-your-actual-secret-key-here
PLAB_MODEL=gemini/gemini-1.5-flash
```

Same file, one letter of difference in the name, and `.gitignore` makes all the difference
between them. Anyone who clones your repo copies `.env.example` to `.env` and pastes in their
own key.

The rule of thumb: **source code, config, docs, and the tests go in. Secrets, generated data,
and machine-specific junk stay out.**

---

## Step 2 — Make the local repo and commit

The repo root is the **project folder** - the one that contains
`prompt_lab/` and this `hosting/` folder. Open PowerShell *there*.

```powershell
git init
```
Creates an empty Git repo here — a hidden `.git` folder that will track your files.

```powershell
git add .
```
Stages every file in the folder *except* the ones `.gitignore` excludes. "Staging" means
marking them to go into the next snapshot. Small catch: `.gitignore` lives at the
repo root, so it governs the whole repo. That's exactly
what you want here - it protects `.env`, which is the file that matters.

```powershell
git commit -m "Initial commit: Prompt Engineering Lab -- five prompt styles, scored"
```
Saves a snapshot of everything staged, with a short message describing it.

Now the single most important check in this whole guide:

```powershell
git status
```

Read the output. You want to see `nothing to commit, working tree clean`. Then run one more,
which lists every file Git is actually tracking:

```powershell
git ls-files
```

Scan that list. You must **not** see `.env` anywhere (`.env.example` is fine and expected). If
`.env` shows up, you committed your secret — go to the troubleshooting section at the bottom
(`Committed .env by accident`) and fix it before you push anything to the internet.

---

## Step 3 — Make the empty repo on GitHub and push

### 3a. Create the empty repo

A "remote" is just a copy of your repo that lives somewhere else — in this case, on GitHub's
servers. You're about to create that remote copy and then connect your local repo to it.

In the browser:

1. Go to github.com, signed in.
2. Top-right, click the **+** then **New repository**.
3. Name it `prompt-engineering-lab` (lowercase, hyphens, no spaces).
4. Add a one-line description: *"Command-line tool that compares five prompt styles on
   support-ticket classification and scores which one wins."*
5. Leave it **Public** — you want recruiters to see it.
6. Do **not** tick "Add a README", "Add .gitignore", or "Add a license". You need the repo
   completely empty, or your first push will collide with the files GitHub adds. Leave every
   box off.
7. Click **Create repository**.

GitHub shows you a setup page with a bunch of commands. Ignore most of it; use what's below.

### 3b. Connect your local repo to GitHub and push

Copy the repo URL from that page — the
`https://github.com/YOURNAME/prompt-engineering-lab.git` one. Then, back in PowerShell at the
project root:

```powershell
git branch -M main
```
Renames your current branch to `main`. A "branch" is a line of development; `main` is GitHub's
default name for the primary one. You'll only ever have the one branch for a project like this.

```powershell
git remote add origin https://github.com/YOURNAME/prompt-engineering-lab.git
```
Tells your local repo where the GitHub copy lives. `origin` is just the conventional nickname
for that URL, so you don't have to type the whole thing every time.

```powershell
git push -u origin main
```
Uploads ("pushes") your commits to GitHub. The `-u` links your local `main` to the remote one,
so next time you can just type `git push` with nothing after it.

The first push pops up a browser window or a login prompt to authenticate with GitHub. Do it.
If it asks for a *password* typed into the terminal, that won't work — GitHub turned off
password auth years ago. Use the browser sign-in it offers (easiest), or a Personal Access
Token as the password (covered in troubleshooting).

Refresh your GitHub repo page. Your files are there. The code is published.

---

## Step 4 — Write a README a recruiter will actually read

A recruiter spends maybe twenty seconds on your repo before deciding whether to keep reading.
The README is the first thing they see (GitHub renders it right under the file list), so it
has to land the project fast.

You already have a strong README at the repo root (`README.md`) - it's the model to
follow for voice and length. GitHub shows the **root** `README.md` first, so make sure its
top sells the project and the full detail sits further down.

Keep it skimmable. Five sections, in this order:

1. **The problem, in one or two sentences.** "Prompt engineering" gets talked about like magic.
   It isn't — it's an engineering choice you can *measure*. This tool runs the same
   classification task through five different prompt styles and scores each one, so you can see
   which prompt actually wins instead of guessing.
2. **What it does.** A short bullet list: classifies support tickets as `billing` /
   `technical` / `other`; compares zero-shot, few-shot, chain-of-thought, role, and
   forced-JSON structured output; prints an accuracy leaderboard, confusion matrices
   (`--confusion`), and the exact tickets each style missed (`--errors`); runs **offline by
   default** with a fake model so no API key is needed, and flips to a real LLM with `--real`.
3. **Results.** Paste the actual leaderboard (Step 4b below) so people see the outcome without
   running anything. This is the section a recruiter remembers.
4. **How to run it.** The exact commands, copy-pasteable:

   ```powershell
   python -m venv .venv ; .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   python generate_data.py
   python -m prompt_lab --confusion
   ```

   Mention the optional `--real` flag needs a free Gemini key in `.env` (point at
   `.env.example`), and that everything else — including the whole test suite — works with no
   key at all.
5. **What you learned.** Two or three honest lines: the five core prompt patterns and when each
   earns its keep; why you keep few-shot examples out of the test set (leakage); validating
   structured JSON output with pydantic; and building an eval — accuracy, parse rate, and a
   confusion matrix that shows the *shape* of the mistakes. This is the section that separates
   "I followed a tutorial" from "I understand what I built."

Don't pad it. A tight README beats a long one.

### 4b. Put the measured results table in the README

This is the single highest-value thing you can add, because it lets someone judge the project
in five seconds without cloning anything. Run the tool and copy its real output in.

```powershell
python -m prompt_lab
```

That prints the leaderboard. Paste it into the README's Results section as a fenced code block
(the monospacing keeps the columns lined up):

````markdown
## Results

Scored on 30 labelled tickets, offline (deterministic — you'll get the same numbers):

```
style               accuracy    parsed
--------------------------------------
chain-of-thought        97%      100%
few-shot                93%      100%
role                    83%      100%
zero-shot               80%      100%
structured-json         80%      100%
```

**Takeaway:** showing examples (few-shot) and asking for reasoning (chain-of-thought) beat
just asking (zero-shot); a persona (role) helps a little; and structured JSON doesn't
necessarily raise accuracy — its win is that every answer parses cleanly, every time.
````

If you'd rather render it as a real Markdown table (nicer on GitHub), the same numbers:

```markdown
| Style             | Accuracy | Parsed |
|-------------------|---------:|-------:|
| chain-of-thought  |     97%  |  100%  |
| few-shot          |     93%  |  100%  |
| role              |     83%  |  100%  |
| zero-shot         |     80%  |  100%  |
| structured-json   |     80%  |  100%  |
```

Either works. The point is that the *outcome* is visible on the repo's front page.

A screenshot helps too — it proves it's a real running tool, not just a table you typed. Run
`python -m prompt_lab --confusion`, press **Win + Shift + S**, drag a box around the terminal
output, paste it into Paint, and save it as `docs/leaderboard.png`. Embed it with
`![Leaderboard and confusion matrices](docs/leaderboard.png)`.

---

## Step 5 — Add CI so the tests run on every push

Right now your tests pass *on your laptop*. CI proves they pass on a clean machine too, every
time you push. "Continuous Integration" is just that idea: every change is automatically
built and tested the moment it lands, so a broken change gets caught in minutes instead of
sitting there until someone trips over it. GitHub shows a green checkmark next to your commits
when the tests pass — recruiters notice it, and it catches the classic "works on my machine"
bug where you forgot to list a dependency.

Here's the part that's a genuine selling point for *this* project: **the tests run offline, so
CI needs no API key.** The lab has a fake-model fallback, so all 27 tests pass without ever
calling a real LLM. That means there are no secrets to configure in GitHub, nothing to leak,
and the CI run is fast and free. A lot of "AI projects" can't be tested in CI at all because
they need a paid key — yours can, honestly, every push. Say so in your README.

In this hosting folder there's a ready-to-use workflow at `github_actions/ci.yml`. A workflow
only runs if it lives at `.github/workflows/` **inside the repo**. So copy it there. From the
project root:

```powershell
mkdir .github\workflows
copy hosting\github_actions\ci.yml .github\workflows\ci.yml
```

Open `.github\workflows\ci.yml` and read the comments — it's annotated line by line. The one
thing worth understanding: because the code sits at the repo root, the workflow installs
from `requirements.txt` and runs pytest straight from the repo root, with no
`working-directory`. Then commit and push:

```powershell
git add .github\workflows\ci.yml
git commit -m "Add GitHub Actions CI to run tests offline on every push"
git push
```

Go to your repo's **Actions** tab. You'll see the workflow running. Click into it to watch the
steps expand live — checkout, install Python, install dependencies, run pytest. Green check
means all 27 tests passed on GitHub's machine. If it goes red, click the failed step and read
the log bottom-up; the real error is usually in the last few lines (a missing dependency in
`requirements.txt` is the most common cause).

Once it's green, add the status badge to the top of your README so the checkmark is visible
without clicking. On the workflow's Actions page there's a `...` menu with **Create status
badge** — it gives you a line of markdown to paste at the very top of `README.md`.

---

## Step 6 — (Optional) a live demo anyone can click

Everything so far is enough for a portfolio. But a *live* demo — a URL a recruiter can open and
see your leaderboard render in a browser, no install — is a real step up. The trick is that
your project is a command-line tool, and the web needs a web page. **Streamlit** bridges that:
it's a Python library that turns a plain script into a web app, and there are two services that
host Streamlit apps for **free**.

You don't rewrite the project. The demo just *imports* your package and calls the same
functions the CLI already calls, then draws the results with Streamlit widgets instead of
`print`.

### 6a. A minimal `app.py`

Put this file at the **repo root** (next to `prompt_lab/`). It runs the offline
evaluation and shows the leaderboard and confusion matrices as tables.

```python
# app.py -- tiny Streamlit front-end for the offline leaderboard.
# Run locally with:  streamlit run app.py
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# The package lives next to this file, so add this folder to the import path.
sys.path.insert(0, str(Path(__file__).parent))

from prompt_lab import CATEGORIES
from prompt_lab.data import load_tickets, load_fewshot_examples
from prompt_lab.evaluate import evaluate_style
from prompt_lab.prompts import STYLES

st.set_page_config(page_title="Prompt Engineering Lab", layout="centered")
st.title("Prompt Engineering Lab")
st.caption(
    "Five prompt styles, one classification task, scored on 30 labelled tickets. "
    "Running OFFLINE with a deterministic fake model -- no API key."
)

# Load data and score every style (offline=True is the default, no key needed).
tickets = load_tickets()
examples = load_fewshot_examples()
scores = [
    evaluate_style(style, tickets, examples=examples, offline=True)
    for style in STYLES
]
scores.sort(key=lambda s: s.accuracy, reverse=True)

# --- Leaderboard table ---
st.subheader("Leaderboard")
leaderboard = pd.DataFrame(
    {
        "style": s.style,
        "accuracy": f"{s.accuracy:.0%}",
        "parsed": f"{s.parse_rate:.0%}",
    }
    for s in scores
)
st.table(leaderboard)

# --- Confusion matrices ---
st.subheader("Confusion matrices")
st.caption("Rows = true category, columns = what the style predicted.")
for s in scores:
    st.markdown(f"**{s.style}** — accuracy {s.accuracy:.0%}")
    matrix = pd.DataFrame(
        [[s.confusion[t][p] for p in CATEGORIES] for t in CATEGORIES],
        index=CATEGORIES,
        columns=CATEGORIES,
    )
    st.dataframe(matrix)
```

Try it locally first (from the project root):

```powershell
python generate_data.py
pip install streamlit pandas
streamlit run app.py
```

It opens a browser tab at `http://localhost:8501` with your leaderboard. If that works
locally, it'll work hosted.

One gotcha: the data CSVs are git-ignored, so they won't exist on the hosting service. Two
clean fixes — either (a) call `generate_data.py` once at the top of `app.py` if the files are
missing, or (b) for the demo only, commit the two tiny CSVs (`data/tickets.csv`,
`data/fewshot_examples.csv`) so they ship with the repo. Option (b) is simplest; they're a few
kilobytes. To force-add a git-ignored file on purpose:

```powershell
git add -f data\tickets.csv data\fewshot_examples.csv
```

### 6b. Host it free — Hugging Face Spaces

Hugging Face **Spaces** hosts small apps for free and has first-class Streamlit support.

1. Make a free account at https://huggingface.co.
2. Click **New Space**. Name it `prompt-engineering-lab`, pick **Streamlit** as the SDK, and
   leave it public.
3. A Space *is* a Git repo. Push your project to it (it gives you the URL), or use the web UI
   to upload `app.py`, the `prompt_lab/` folder, and a `requirements.txt` that lists
   what the app needs — at minimum `streamlit`, `pandas`, `pydantic`.
4. The Space builds and gives you a public URL like
   `https://huggingface.co/spaces/YOURNAME/prompt-engineering-lab`. That's your live demo.

### 6c. Or — Streamlit Community Cloud

If your code is already on GitHub, this is even less work:

1. Go to https://share.streamlit.io and sign in with GitHub.
2. Click **New app**, pick your `prompt-engineering-lab` repo, and set the main file to
   `app.py`.
3. It reads a `requirements.txt` for the app's dependencies (`streamlit`, `pandas`,
   `pydantic`), builds, and gives you a public `*.streamlit.app` URL.

### 6d. If you want the demo to use a REAL model

The offline demo is the safe default and needs no secret. If you later want a "run it live
against Gemini" button, you'd call `evaluate_style(..., offline=False)`. That needs an API
key — and here's the rule that never changes: **the key goes in the hosting service's secrets
manager, never in your code.** On Hugging Face it's the Space's **Settings > Secrets** (add
`GEMINI_API_KEY` there); on Streamlit Cloud it's the app's **Settings > Secrets**. The service
injects it as an environment variable at runtime, so your public `app.py` never contains the
key. Same golden rule as `.env`, just in the cloud.

### 6e. Link the demo from your README

Once it's live, put the URL at the top of your README so nobody misses it:

```markdown
**Live demo:** https://YOURNAME-prompt-engineering-lab.hf.space
```

A clickable demo plus a green CI badge plus a results table is a genuinely strong portfolio
page.

---

## Step 7 — Pin the repo on your profile

By default your GitHub profile shows repos in whatever order. Pinning puts the good ones up
top so a recruiter sees them first.

1. Go to your profile page (`github.com/YOURNAME`).
2. Find the **Customize your pins** link (or **Pin** on a repo card).
3. Tick `prompt-engineering-lab`. You can pin up to six.
4. Save.

Now it's one of the first things on your profile. Done.

---

## Optional — publishing it for others to install

You don't need this for a portfolio, but it's worth knowing the next step exists.

Because the repo root has a `pyproject.toml` with a `prompt-lab` console script, it's
already shaped like a real installable package. Later, you could publish it to **PyPI** (the
Python Package Index) so anyone can `pip install prompt-lab`, or let people run it in an
isolated environment with **pipx**. That involves making a PyPI account, building the package,
and uploading with a tool called `twine`. It's a good exercise once the repo is polished — but
don't let it block you now. A clean GitHub repo with green CI is what gets you the interview.

---

## Common Git mistakes (troubleshooting)

**You committed `.env` by accident.** First, stop and treat the key as compromised — go to the
provider (Google AI Studio, Groq, Anthropic) and **revoke/rotate it**, because if you already
pushed, it's already public. Then remove the file from Git while keeping it on disk:

```powershell
git rm --cached .env
git commit -m "Remove committed .env"
git push
```

Confirm `.env` is in `.gitignore` so it doesn't come back. Note that `git rm --cached` only
removes it going forward — the key still sits in your Git *history*, which is exactly why you
rotate the key rather than relying on deletion. (Fully scrubbing history is possible with
tools like `git filter-repo`, but rotating the key is the real fix.)

**`error: failed to push` / push rejected.** The remote has commits your local repo doesn't —
almost always because you let GitHub add a README or license when creating the repo. Pull and
replay your work on top, then push:

```powershell
git pull origin main --rebase
git push
```

Next time, create the repo completely empty.

**A huge file won't push (over ~100 MB).** GitHub rejects files above 100 MB. You probably
staged something that should've been ignored — a `.venv`, a model file. Remove it from staging,
add it to `.gitignore`, and commit again:

```powershell
git rm --cached path\to\the\big\file
```

The generated ticket CSVs are tiny (a few KB), so they're fine to commit if you want them for
the demo.

**Authentication fails on push.** GitHub no longer accepts your account password in the
terminal. Two clean ways to fix it:

- **GitHub CLI (easiest):** install it from https://cli.github.com, then run `gh auth login`
  and follow the browser prompts. It handles auth for all future Git commands.
- **Personal Access Token:** on github.com go to **Settings > Developer settings > Personal
  access tokens > Tokens (classic) > Generate new token**, give it the `repo` scope, copy the
  token, and paste it as the *password* when Git prompts you. Treat the token like a password —
  don't commit it anywhere.

**`git: command not found` after installing.** You're in a terminal that opened before the
install. Close every PowerShell window and open a fresh one.

**CI is red but the tests pass on my laptop.** Read the Actions log bottom-up. The usual cause
is a dependency you have installed locally but forgot to list in
`requirements.txt` - CI starts from nothing, so it only has what's listed.
Add the missing package, commit, push, and it re-runs automatically.
