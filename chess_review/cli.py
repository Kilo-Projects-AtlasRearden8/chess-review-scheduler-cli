"""Command-line interface for the chess review scheduler."""

from __future__ import annotations

import argparse
import sys
from datetime import date
from typing import List, Optional

from chess_review.scheduler import (
    ReviewItem,
    CATEGORIES,
    today,
    sm2_next,
    due_items,
    upcoming_items,
    filter_by_category,
)
from chess_review.storage import Storage, DEFAULT_PATH


def _new_id(items: List[ReviewItem]) -> str:
    existing = {item.id for item in items}
    number = 1
    while f"item-{number}" in existing:
        number += 1
    return f"item-{number}"


def _parse_date(value: Optional[str], what: str) -> date:
    if value is None:
        return today()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        print(f"error: invalid {what} date {value!r} (expected YYYY-MM-DD)", file=sys.stderr)
        sys.exit(2)


def _validate_quality(value: int) -> int:
    if not 0 <= value <= 5:
        print(f"error: quality must be between 0 and 5, got {value}", file=sys.stderr)
        sys.exit(2)
    return value


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

    p_list = sub.add_parser("list", help="List all review items")
    p_list.add_argument("--category", choices=list(CATEGORIES), help="Filter by category")

    p_due = sub.add_parser("due", help="List items due for review")
    p_due.add_argument("--on", default=None, help="Check due status as of this date (YYYY-MM-DD)")
    p_due.add_argument("--category", choices=list(CATEGORIES), help="Filter by category")

    p_upcoming = sub.add_parser("upcoming", help="List items due within the next N days")
    p_upcoming.add_argument("days", type=int, help="Number of days ahead to look")
    p_upcoming.add_argument("--on", default=None, help="Start date (YYYY-MM-DD), defaults to today")
    p_upcoming.add_argument("--category", choices=list(CATEGORIES), help="Filter by category")

    p_review = sub.add_parser("review", help="Show details of a specific item")
    p_review.add_argument("id", help="Item id")

    p_grade = sub.add_parser("grade", help="Record a review grade (0-5) for an item")
    p_grade.add_argument("id", help="Item id")
    p_grade.add_argument("quality", type=int, help="Recall quality 0-5")
    p_grade.add_argument("--on", default=None, help="Review date (YYYY-MM-DD), defaults to today")

    p_delete = sub.add_parser("delete", help="Delete a review item by id")
    p_delete.add_argument("id", help="Item id")

    p_export = sub.add_parser("export", help="Export items to JSON or CSV")
    p_export.add_argument("format", choices=["json", "csv"], help="Export format")
    p_export.add_argument("dest", help="Destination file path")

    p_import = sub.add_parser("import", help="Import items from JSON or CSV (skips duplicate ids)")
    p_import.add_argument("format", choices=["json", "csv"], help="Import format")
    p_import.add_argument("src", help="Source file path")

    return parser


def _print_item_row(item: ReviewItem, marker: str = "") -> None:
    print(f"{marker}{item.id}  {item.category:<8} {item.title}  next: {item.next_review}")


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
        if args.category:
            items = filter_by_category(items, args.category)
        if not items:
            print("no items")
            return 0
        for item in items:
            marker = "DUE " if date.fromisoformat(item.next_review) <= today() else "    "
            _print_item_row(item, marker)
        return 0

    if args.command == "due":
        on = _parse_date(args.on, "due")
        items = storage.list_due(on.isoformat())
        if args.category:
            items = filter_by_category(items, args.category)
        if not items:
            print("nothing due")
            return 0
        for item in items:
            _print_item_row(item)
        return 0

    if args.command == "upcoming":
        if args.days < 0:
            print("error: days must be zero or more", file=sys.stderr)
            return 2
        on = _parse_date(args.on, "upcoming")
        items = storage.list_all()
        if args.category:
            items = filter_by_category(items, args.category)
        items = upcoming_items(items, args.days, on)
        if not items:
            print("nothing upcoming")
            return 0
        for item in items:
            try:
                nr = date.fromisoformat(item.next_review)
            except ValueError:
                nr = on
            days_away = (nr - on).days
            print(f"{item.id}  {item.category:<8} {item.title}  in {days_away} day(s) ({item.next_review})")
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
        print(f"no item with id {args.id!r}", file=sys.stderr)
        return 1

    if args.command == "grade":
        quality = _validate_quality(args.quality)
        try:
            item = storage.grade(args.id, quality, args.on)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        print(
            f"graded {item.id} quality={quality} "
            f"next: {item.next_review} (interval {item.interval} days, ease {item.ease_factor})"
        )
        return 0

    if args.command == "delete":
        try:
            removed = storage.delete(args.id)
        except KeyError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        print(f"deleted {removed.id}: {removed.title} [{removed.category}]")
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
