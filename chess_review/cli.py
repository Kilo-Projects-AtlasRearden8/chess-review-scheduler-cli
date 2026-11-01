"""Command-line interface for the chess review scheduler."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from typing import List, Optional

from chess_review.scheduler import ReviewItem, CATEGORIES, today, sm2_next, due_items
from chess_review.storage import Storage, DEFAULT_PATH


def _new_id(items: List[ReviewItem]) -> str:
    existing = {item.id for item in items}
    number = 1
    while f"item-{number}" in existing:
        number += 1
    return f"item-{number}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chess-review",
        description="Local-first spaced-repetition scheduler for chess study.",
    )
    parser.add_argument(
        "--data", default=None, help="Path to the JSON data file (default: ~/.chess_review/data.json)"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="Add a new chess review item")
    p_add.add_argument("--category", required=True, choices=list(CATEGORIES), help="opening, tactic, or endgame")
    p_add.add_argument("--title", required=True, help="Title of the item")
    p_add.add_argument("--fen", default="", help="FEN position string")
    p_add.add_argument("--moves", default="", help="Moves / variation")
    p_add.add_argument("--notes", default="", help="Free-form notes")

    sub.add_parser("list", help="List all review items")
    p_due = sub.add_parser("due", help="List items due for review")
    p_due.add_argument("--on", default=None, help="Check due status as of this date (YYYY-MM-DD)")

    p_review = sub.add_parser("review", help="Show details of a specific item")
    p_review.add_argument("id", help="Item id")

    p_grade = sub.add_parser("grade", help="Record a review grade (0-5) for an item")
    p_grade.add_argument("id", help="Item id")
    p_grade.add_argument("quality", type=int, help="Recall quality 0-5")
    p_grade.add_argument("--on", default=None, help="Review date (YYYY-MM-DD), defaults to today")

    p_export = sub.add_parser("export", help="Export items to JSON or CSV")
    p_export.add_argument("format", choices=["json", "csv"], help="Export format")
    p_export.add_argument("dest", help="Destination file path")

    p_import = sub.add_parser("import", help="Import items from JSON or CSV")
    p_import.add_argument("format", choices=["json", "csv"], help="Import format")
    p_import.add_argument("src", help="Source file path")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    storage = Storage(args.data)

    if args.command == "add":
        items = storage.load()
        item = ReviewItem(
            id=_new_id(items),
            category=args.category,
            title=args.title,
            fen=args.fen,
            moves=args.moves,
            notes=args.notes,
            next_review=today().isoformat(),
        )
        item.validate()
        storage.add(item)
        print(f"added {item.id}: {item.title} [{item.category}]")
        return 0

    if args.command == "list":
        items = storage.list_all()
        if not items:
            print("no items")
            return 0
        for item in items:
            marker = "DUE " if date.fromisoformat(item.next_review) <= today() else "    "
            print(
                f"{marker}{item.id}  {item.category:<8} {item.title}  next: {item.next_review}"
            )
        return 0

    if args.command == "due":
        items = storage.list_due(args.on)
        if not items:
            print("nothing due")
            return 0
        for item in items:
            print(
                f"{item.id}  {item.category:<8} {item.title}  next: {item.next_review}"
            )
        return 0

    if args.command == "review":
        items = storage.load()
        for item in items:
            if item.id == args.id:
                print(f"id:        {item.id}")
                print(f"category:  {item.category}")
                print(f"title:     {item.title}")
                print(f"fen:       {item.fen}")
                print(f"moves:     {item.moves}")
                print(f"notes:     {item.notes}")
                print(f"created:   {item.created}")
                print(f"next:      {item.next_review}")
                print(f"interval:  {item.interval} days")
                print(f"reps:      {item.repetitions}")
                print(f"ease:      {item.ease_factor}")
                return 0
        print(f"no item with id {args.id!r}")
        return 1

    if args.command == "grade":
        try:
            item = storage.grade(args.id, args.quality, args.on)
        except KeyError as exc:
            print(str(exc))
            return 1
        except ValueError as exc:
            print(f"error: {exc}")
            return 1
        print(
            f"graded {item.id} quality={args.quality} "
            f"next: {item.next_review} (interval {item.interval} days, ease {item.ease_factor})"
        )
        return 0

    if args.command == "export":
        if args.format == "json":
            storage.export_json(args.dest)
        else:
            storage.export_csv(args.dest)
        print(f"exported to {args.dest}")
        return 0

    if args.command == "import":
        if args.format == "json":
            storage.import_json(args.src)
        else:
            storage.import_csv(args.src)
        print(f"imported from {args.src}")
        return 0

    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
