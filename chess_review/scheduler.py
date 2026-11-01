"""Data model and SM-2 spaced-repetition scheduler for chess review items."""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import List, Optional


CATEGORIES = ("opening", "tactic", "endgame")


def today() -> date:
    return date.today()


@dataclass
class ReviewItem:
    """A single chess review item with spaced-repetition state."""

    id: str
    category: str
    title: str
    fen: str = ""
    moves: str = ""
    notes: str = ""
    created: str = field(default_factory=lambda: today().isoformat())
    next_review: str = field(default_factory=lambda: today().isoformat())
    interval: int = 0
    repetitions: int = 0
    ease_factor: float = 2.5

    def validate(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"category must be one of {CATEGORIES}, got {self.category!r}")
        if not self.title.strip():
            raise ValueError("title is required")
        try:
            date.fromisoformat(self.created)
            date.fromisoformat(self.next_review)
        except ValueError as exc:
            raise ValueError("created and next_review must be ISO dates (YYYY-MM-DD)") from exc

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ReviewItem":
        return cls(**{k: data[k] for k in cls.__dataclass_fields__ if k in data})


def sm2_next(item: ReviewItem, quality: int, review_date: date) -> ReviewItem:
    """Advance a review item using the SM-2 algorithm.

    quality: integer 0-5, where 5 = perfect recall, 0 = complete blackout.
    """
    if not 0 <= quality <= 5:
        raise ValueError("quality must be between 0 and 5")

    ef = item.ease_factor
    reps = item.repetitions
    interval = item.interval

    if quality < 3:
        reps = 1
        interval = 1
    else:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        reps += 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if ef < 1.3:
        ef = 1.3

    return ReviewItem(
        id=item.id,
        category=item.category,
        title=item.title,
        fen=item.fen,
        moves=item.moves,
        notes=item.notes,
        created=item.created,
        next_review=(review_date + timedelta(days=interval)).isoformat(),
        interval=interval,
        repetitions=reps,
        ease_factor=round(ef, 2),
    )


def due_items(items: List[ReviewItem], on: Optional[date] = None) -> List[ReviewItem]:
    """Return items whose next_review is on or before `on` (default: today)."""
    if on is None:
        on = today()
    result = []
    for item in items:
        try:
            nr = date.fromisoformat(item.next_review)
        except ValueError:
            nr = on  # treat malformed dates as due
        if nr <= on:
            result.append(item)
    return result
