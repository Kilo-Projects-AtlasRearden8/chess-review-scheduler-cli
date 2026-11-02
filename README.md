# Chess Review Scheduler

A friendly, local-first command-line tool for chess study — openings, tactics,
and endgames — built and maintained by **Asdale Dynamics, LLC**.

This tool helps you decide *what to review tomorrow* using spaced repetition, a
learning method that shows you material right before you're likely to forget it.
You add chess positions, puzzles, or theory you want to remember, grade how well
you recalled each one, and the tool schedules your next review automatically.

Everything stays on your own computer. No API keys, no accounts, no network, no
personal data. Just you, your chess, and a simple JSON file you control.

## Who this is for

Chess players of any strength who want a simple, tested way to keep their
openings, tactics, and endgames fresh. Beginners are especially welcome — the
interface is plain English, step by step, never condescending.

This is one of the small open-source tools Asdale Dynamics, LLC (Indiana,
formed October 2026) publishes alongside beginner-friendly AI education, books,
and small-business guides. Asdale Dynamics, LLC is run by Dylan Asdale, a
registered nurse turned AI author whose book *The Massive AI Manual* and hub
site dylanasdale.github.io explain AI "like a friend would."

## Features

- Spaced-repetition scheduling (SM-2) with review dates, intervals, and ease factors
- Three categories: opening, tactic, endgame
- FEN position, move text, and free-form notes for every item
- Commands: `add`, `list`, `due`, `upcoming`, `review`, `grade`, `delete`, `export`, `import`
- JSON storage; export and import in JSON or CSV
- Fully local-first: your data lives in a JSON file you choose
- Zero dependencies beyond the Python standard library
- Tested with 30+ automated tests; no secrets, keys, or personal data anywhere

## Install

```bash
git clone <this repo>
cd chess-review-scheduler-cli
python3 -m venv venv
./venv/bin/pip install -e .
```

Or run without installing:

```bash
python3 -m chess_review.cli --help
```

After `pip install -e .`, the `chess-review` command is available everywhere.

## Quick start

Create a data file in your project folder (recommended) and add your first item:

```bash
chess-review --data chess.json add --category tactic --title "Back-rank mate" --notes "rook on the 8th rank"
chess-review --data chess.json add --category opening --title "Italian Game" --notes "1.e4 e5 2.Nf3 Nc6 3.Bc4"
chess-review --data chess.json add --category endgame --title "Lucena position"
```

See everything you're studying:

```bash
chess-review --data chess.json list
```

Items due today are marked `DUE`. See only what's due:

```bash
chess-review --data chess.json due
```

See what's coming up in the next week:

```bash
chess-review --data chess.json upcoming 7
```

Filter by category (opening / tactic / endgame):

```bash
chess-review --data chess.json list --category tactic
chess-review --data chess.json due --category endgame
```

## Grading your reviews

When you review an item, grade yourself from 0 to 5:

- 5 — perfect recall, no hesitation
- 4 — recalled with a little hesitation
- 3 — recalled with serious difficulty
- 2 — wrong, but the answer seemed familiar once you saw it
- 1 — wrong, but recognized the position
- 0 — completely forgot / blackout

Record a grade:

```bash
chess-review --data chess.json grade item-1 5
```

The tool moves the item's next review further out (or resets it to tomorrow if
you scored below 3). Inspect an item anytime:

```bash
chess-review --data chess.json review item-1
```

Remove an item you no longer want to study:

```bash
chess-review --data chess.json delete item-2
```

## Backing up and sharing your library

Export to JSON (full data) or CSV (spreadsheet-friendly):

```bash
chess-review --data chess.json export json backup.json
chess-review --data chess.json export csv library.csv
```

Import later (items already in your file are skipped by id, so importing twice
won't create duplicates):

```bash
chess-review --data chess.json import json backup.json
chess-review --data chess.json import csv library.csv
```

The data file defaults to `~/.chess_review/data.json`. Use `--data` or the
`CHESS_REVIEW_DATA` environment variable to keep a file inside your project —
handy for version control or syncing between computers.

## What the data file looks like

Each item is plain JSON. You can edit it by hand if you need to:

```json
{
  "id": "item-1",
  "category": "tactic",
  "title": "Back-rank mate",
  "fen": "r1bqkbnr/pppp1ppp/2n5/1Bb2p2/4P3/5N2/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
  "moves": "",
  "notes": "rook on the 8th rank",
  "created": "2026-11-02",
  "next_review": "2026-11-03",
  "interval": 1,
  "repetitions": 1,
  "ease_factor": 2.6
}
```

## Tests

```bash
python3 -m pytest -q
```

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC is an Indiana LLC founded by Dylan Asdale, a registered
nurse turned AI author and founder. His book *The Massive AI Manual* and hub
site dylanasdale.github.io explain AI "like a friend would": plain English,
step by step, never condescending. The LLC focuses on beginner-friendly AI
education, open-source tools, small-business and author tools, and accessible
life-admin helpers — including chess tools like this one.

This tool is educational and practical software; it is not medical advice.
