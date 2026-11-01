# Chess Review Scheduler

A local-first, spaced-repetition command-line tool for chess study — openings,
tactics, and endgames — built and maintained by **Asdale Dynamics, LLC**.

Track review dates for chess material using the SM-2 spaced-repetition
algorithm, export your library to JSON or CSV, and keep everything on your own
machine. No API keys, no accounts, no network, no personal data.

## Who this is for

Chess players of any strength who want a simple, tested way to decide *what to
review tomorrow*. Beginners welcome — the interface is plain English and
step by step, never condescending. This is one of the small open-source tools
Asdale Dynamics, LLC (Indiana, formed October 2026) publishes alongside
beginner-friendly AI education, books, and small-business guides.

## Features

- Spaced-repetition scheduling (SM-2) with review dates, intervals, and ease factors
- Three categories: opening, tactic, endgame
- FEN positions, move text, and free-form notes per item
- `add`, `list`, `due`, `review`, `grade`, `export`, `import` commands
- JSON storage and JSON/CSV export/import
- Fully local-first: your data lives in a JSON file you control
- Zero dependencies beyond the Python standard library
- Test suite included; no secrets, keys, or personal data anywhere

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

The console script `chess-review` is available after `pip install -e .`.

## Usage

Add an item:

```bash
chess-review --data chess.json add --category tactic --title "Back-rank mate" --notes "rook on the 8th rank"
```

List everything (items due today are marked `DUE`):

```bash
chess-review --data chess.json list
```

Show only items due for review:

```bash
chess-review --data chess.json due
```

Grade a recalled item (quality 0–5; 5 = perfect):

```bash
chess-review --data chess.json grade item-1 5
```

Inspect one item:

```bash
chess-review --data chess.json review item-1
```

Export your library:

```bash
chess-review --data chess.json export json backup.json
chess-review --data chess.json export csv library.csv
```

Import items (replaces nothing; appends and saves):

```bash
chess-review --data chess.json import json backup.json
chess-review --data chess.json import csv library.csv
```

The data file defaults to `~/.chess_review/data.json`. Use `--data` or the
`CHESS_REVIEW_DATA` environment variable to choose another location — handy for
keeping a data file inside your project.

## Example data file

Each item is a plain JSON object:

```json
{
  "id": "item-1",
  "category": "tactic",
  "title": "Back-rank mate",
  "fen": "r1bqkbnr/pppp1ppp/2n5/1Bb2p2/4P3/5N2/PPPP1PPP/RNBQK1NR w KQkq - 4 4",
  "moves": "1. e4 e5 2. Nf3 Nc6 3. Bc4",
  "notes": "Classical open game",
  "created": "2026-11-01",
  "next_review": "2026-11-02",
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
