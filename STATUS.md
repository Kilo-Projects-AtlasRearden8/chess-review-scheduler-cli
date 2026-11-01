# STATUS

## What was built

`chess-review-scheduler-cli`: a local-first, zero-dependency Python CLI for
spaced-repetition chess study (openings, tactics, endgames) using the SM-2
algorithm.

Project layout:
- `pyproject.toml` — project metadata and `chess-review` console entry point
- `chess_review/__init__.py` — package marker
- `chess_review/scheduler.py` — `ReviewItem` data model, SM-2 scheduler, due-date filtering
- `chess_review/storage.py` — JSON storage, JSON/CSV export and import
- `chess_review/cli.py` — argparse CLI: `add`, `list`, `due`, `review`, `grade`, `export`, `import`
- `tests/test_chess_review.py` — 18 tests covering model, scheduler edge cases, storage, and CLI
- `tests/conftest.py` — import seed fixture for CSV/JSON import tests
- `LICENSE` — MIT, copyright `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — usage docs, credits Asdale Dynamics, LLC

Commands:
- `add --category <opening|tactic|endgame> --title T [--fen F] [--moves M] [--notes N]`
- `list` — all items, `DUE` marker for items due today
- `due [--on YYYY-MM-DD]` — items due for review
- `review ID` — full item detail
- `grade ID 0-5 [--on YYYY-MM-DD]` — record recall quality, advances schedule via SM-2
- `export <json|csv> PATH`
- `import <json|csv> PATH`

Data file defaults to `~/.chess_review/data.json`, overridable with `--data` or
`CHESS_REVIEW_DATA`. No network, no API keys, no personal data.

## How to run

```bash
cd chess-review-scheduler-cli
python3 -m venv venv
./venv/bin/pip install -e .
chess-review --data chess.json add --category tactic --title "Back-rank mate"
chess-review --data chess.json due
chess-review --data chess.json grade item-1 5
chess-review --data chess.json export json backup.json
```

Or without installing: `python3 -m chess_review.cli --help`.

## Verification results

- `python3 -m pytest -q`: **18 passed** (model validation, SM-2 first/repeat/forgotten reviews, ease floor, due filtering, JSON/CSV storage, export/import, CLI end-to-end including unknown-id errors)
- `pip install -e .` in a clean venv: **success**
- `chess-review --help` and smoke test of add/list/due/grade/review/export (json+csv): **success**, output matches expected SM-2 behavior (quality 5 → interval 1, next review +1 day, ease 2.6)
- LICENSE copyright line verified exactly: `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC
- No `.github/workflows` files, no secrets, keys, or personal data in any file

## Known gaps

- No web UI or GUI; CLI only
- No item deletion or edit command (items can be removed by editing the JSON file directly)
- No duplicate detection on import (import appends)
- No review session mode that walks through due items interactively
- SM-2 is the only scheduling algorithm; no FSRS or Leitner option
- Data file is a single JSON file; no concurrency locking
- Tests use the real system date via `date.today()`; some assertions depend on "today"
