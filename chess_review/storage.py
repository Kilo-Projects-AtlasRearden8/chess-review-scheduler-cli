"""Storage for chess review items: JSON backend with CSV/JSON export."""

from __future__ import annotations

import csv
import json
import os
from datetime import date
from typing import List, Optional

from chess_review.scheduler import ReviewItem, due_items, today, sm2_next


DEFAULT_DIR = os.path.join(os.path.expanduser("~"), ".chess_review")
DEFAULT_PATH = os.path.join(DEFAULT_DIR, "data.json")


class Storage:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.environ.get("CHESS_REVIEW_DATA") or DEFAULT_PATH

    def _ensure_dir(self) -> None:
        directory = os.path.dirname(self.path)
        if directory and not os.path.isdir(directory):
            os.makedirs(directory, exist_ok=True)

    def load(self) -> List[ReviewItem]:
        if not os.path.exists(self.path):
            return []
        with open(self.path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, list):
            return []
        items = []
        for entry in raw:
            try:
                item = ReviewItem.from_dict(entry)
                item.validate()
                items.append(item)
            except Exception:
                # Skip malformed entries rather than crashing the whole library.
                continue
        return items

    def save(self, items: List[ReviewItem]) -> None:
        self._ensure_dir()
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump([item.to_dict() for item in items], fh, indent=2)

    def add(self, item: ReviewItem) -> List[ReviewItem]:
        items = self.load()
        items.append(item)
        self.save(items)
        return items

    def grade(self, item_id: str, quality: int, on: Optional[str] = None) -> ReviewItem:
        items = self.load()
        for index, item in enumerate(items):
            if item.id == item_id:
                review_date = date.fromisoformat(on) if on else today()
                items[index] = sm2_next(item, quality, review_date)
                self.save(items)
                return items[index]
        raise KeyError(f"no item with id {item_id!r}")

    def list_all(self) -> List[ReviewItem]:
        return self.load()

    def list_due(self, on: Optional[str] = None) -> List[ReviewItem]:
        review_date = date.fromisoformat(on) if on else today()
        return due_items(self.load(), review_date)

    def export_json(self, dest: str) -> None:
        items = self.load()
        with open(dest, "w", encoding="utf-8") as fh:
            json.dump([item.to_dict() for item in items], fh, indent=2)

    def export_csv(self, dest: str) -> None:
        items = self.load()
        fields = [
            "id", "category", "title", "fen", "moves", "notes",
            "created", "next_review", "interval", "repetitions", "ease_factor",
        ]
        with open(dest, "w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            for item in items:
                writer.writerow(item.to_dict())

    def import_json(self, src: str) -> List[ReviewItem]:
        with open(src, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if not isinstance(raw, list):
            raise ValueError("JSON import must contain a list of items")
        items = self.load()
        for entry in raw:
            item = ReviewItem.from_dict(entry)
            item.validate()
            items.append(item)
        self.save(items)
        return items

    def import_csv(self, src: str) -> List[ReviewItem]:
        items = self.load()
        with open(src, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                item = ReviewItem(
                    id=row["id"],
                    category=row["category"],
                    title=row["title"],
                    fen=row.get("fen", ""),
                    moves=row.get("moves", ""),
                    notes=row.get("notes", ""),
                    created=row.get("created", today().isoformat()),
                    next_review=row.get("next_review", today().isoformat()),
                    interval=int(row.get("interval", 0) or 0),
                    repetitions=int(row.get("repetitions", 0) or 0),
                    ease_factor=float(row.get("ease_factor", 2.5) or 2.5),
                )
                item.validate()
                items.append(item)
        self.save(items)
        return items
