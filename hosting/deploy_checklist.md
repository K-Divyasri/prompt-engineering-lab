# Deploy checklist — Prompt Engineering Lab

This is the project's "definition of done." Walk it top to bottom. Don't tick a box you
haven't actually verified by running the command — "should work" isn't the same as "works."

## Runs locally

- [ ] Fresh virtual environment, dependencies installed cleanly (from the repo root):
      `python -m venv .venv ; .\.venv\Scripts\Activate.ps1` then `pip install -r requirements.txt`
- [ ] The dataset generates without error:
      `python generate_data.py` (writes `data/tickets.csv` + `data/fewshot_examples.csv`)
- [ ] The leaderboard runs offline, no API key:
      `python -m prompt_lab`
- [ ] The confusion matrices print:
      `python -m prompt_lab --confusion`
- [ ] (Optional) The `--real` flag works with a key in `.env`, OR is left alone — offline is
      the default and needs nothing.

## Tests pass

- [ ] `pytest` run from the repo root is all green (27 tests, all offline).
- [ ] You ran it in the fresh venv, not just your everyday one, so you know the deps are complete.

## README is recruiter-ready

- [ ] A root `README.md` exists and covers: the problem, what the tool does, the results, how
      to run it, and what you learned.
- [ ] The measured **results table** (accuracy leaderboard) is pasted in, so the outcome is
      visible without running anything.
- [ ] A terminal screenshot of the leaderboard/confusion output is embedded
      (`docs/leaderboard.png` or similar).
- [ ] The CI status badge is at the top.

## Secrets are clean

- [ ] `.gitignore` contains `.env` (plus `.venv/`, `__pycache__/`, `data/*.csv`).
- [ ] `git status` shows `.env` is NOT tracked.
- [ ] `git ls-files` output contains NO `.env` (only `.env.example`). If `.env` is there,
      remove it and rotate the key — see the hosting guide's troubleshooting section.
- [ ] No API key is hardcoded anywhere in the source.

## Pushed to GitHub

- [ ] Repo created empty on github.com (no auto README/license), named
      `prompt-engineering-lab`, public.
- [ ] `git init` → `git add .` → `git commit` → `git branch -M main` →
      `git remote add origin ...` → `git push -u origin main` all done (from the project root).
- [ ] Files visible on the GitHub repo page after a refresh.

## CI is green

- [ ] `.github/workflows/ci.yml` is committed and pushed.
- [ ] The Actions tab shows a completed run with a green checkmark.
- [ ] The run used NO secrets (the tests are offline) — confirm it passed without any API key
      configured. That's a selling point; mention it in the README.
- [ ] If it was red, you read the log and fixed the cause (usually a missing dep in
      `requirements.txt`), then re-ran to green.

## Repo pinned

- [ ] `prompt-engineering-lab` is pinned on your GitHub profile so it shows up first.

## (Optional) Live demo

- [ ] `app.py` runs locally: `streamlit run app.py` shows the leaderboard in a browser.
- [ ] Deployed free to Hugging Face Spaces or Streamlit Community Cloud.
- [ ] The demo's data CSVs are available there (committed with `git add -f`, or generated on
      startup).
- [ ] If the demo uses `--real`, the API key is set as a Space/app **secret** — never in code.
- [ ] The live demo URL is added to the top of the README.

When every box is ticked, the project is done and presentable. Send the repo link with
confidence.
