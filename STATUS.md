# STATUS

## What was built

`chess-review-scheduler-cli`: a local-first, zero-dependency Python CLI for
spaced-repetition chess study (openings, tactics, endgames) using the SM-2
algorithm. Built and maintained by Asdale Dynamics, LLC.

Project layout:
- `pyproject.toml` — project metadata and `chess-review` console entry point
- `chess_review/__init__.py` — package marker
- `chess_review/scheduler.py` — `ReviewItem` data model, SM-2 scheduler,
  due/upcoming filtering, category filtering
- `chess_review/storage.py` — JSON storage, JSON/CSV export/import, duplicate
  detection on import, item delete
- `chess_review/cli.py` — argparse CLI: `add`, `list`, `due`, `upcoming`,
  `review`, `grade`, `delete`, `export`, `import` with clean error handling
- `tests/test_chess_review.py` — 32 tests covering model, scheduler edge cases,
  storage, CLI commands, filters, and error handling
- `tests/conftest.py` — import seed fixture for CSV/JSON import tests
- `LICENSE` — MIT, copyright `Copyright (c) 2026 Asdale Dynamics, LLC`
- `README.md` — beginner-friendly usage docs, credits Asdale Dynamics, LLC
- `.gitignore` — standard Python ignore patterns
- `STATUS.md` — this file

Commands:
- `add --category <opening|tactic|endgame> --title T [--fen F] [--moves M] [--notes N]`
- `list [--category C]` — all items, `DUE` marker for items due today
- `due [--on YYYY-MM-DD] [--category C]` — items due for review
- `upcoming N [--on YYYY-MM-DD] [--category C]` — items due within N days
- `review ID` — full item detail
- `grade ID 0-5 [--on YYYY-MM-DD]` — record recall quality, advances schedule via SM-2
- `delete ID` — remove a review item
- `export <json|csv> PATH`
- `import <json|csv> PATH` — skips items whose id already exists

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

- `python3 -m pytest -q`: **32 passed** (model validation, SM-2 first/repeat/forgotten reviews, ease floor, due/upcoming filtering, category filtering, JSON/CSV storage, export/import, duplicate-detection import, delete, CLI end-to-end including invalid quality/date errors and unknown-id errors)
- CLI entry point `chess-review` works after `pip install -e .` in a clean venv
- `chess-review --help` lists all 9 commands; smoke test of add/list/due/upcoming/review/grade/delete/export (json+csv) produced correct SM-2 output (quality 5 → interval 1, next review +1 day, ease 2.6)
- Errors print to stderr with clean messages; invalid quality/date exits code 2; unknown id exits code 1
- LICENSE copyright line verified exactly: `Copyright (c) 2026 Asdale Dynamics, LLC`
- README credits Asdale Dynamics, LLC throughout, beginner-friendly tone
- No `.github/workflows` files; no secrets, keys, or personal data in any file
- Committed as existing git identity (Dylan Asdale), plain message, no co-author trailers

## Known gaps

- No web UI or GUI; CLI only
- No item edit command (fields can be changed by editing the JSON file directly)
- No interactive review session that walks through due items one by one
- SM-2 is the only scheduling algorithm; no FSRS or Leitner option
- Single JSON data file; no concurrency locking for simultaneous access
- Tests use `date.today()` for "today"-relative assertions
- No duplicate-title detection (only duplicate-id on import)
