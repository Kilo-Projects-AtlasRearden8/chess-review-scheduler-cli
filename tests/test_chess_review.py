"""Tests for the chess review scheduler."""

from datetime import date
from unittest import TestCase

from chess_review.scheduler import ReviewItem, CATEGORIES, sm2_next, due_items, today
from chess_review.storage import Storage


class SchedulerTests(TestCase):
    def test_categories(self):
        self.assertEqual(CATEGORIES, ("opening", "tactic", "endgame"))

    def test_item_defaults(self):
        item = ReviewItem(id="x", category="tactic", title="mate in one")
        self.assertEqual(item.category, "tactic")
        self.assertEqual(item.interval, 0)
        self.assertEqual(item.repetitions, 0)
        self.assertEqual(item.ease_factor, 2.5)
        self.assertEqual(item.next_review, today().isoformat())

    def test_validation_bad_category(self):
        item = ReviewItem(id="x", category="blunder", title="t")
        with self.assertRaises(ValueError):
            item.validate()

    def test_validation_empty_title(self):
        item = ReviewItem(id="x", category="tactic", title="   ")
        with self.assertRaises(ValueError):
            item.validate()

    def test_sm2_first_review_easy(self):
        item = ReviewItem(id="x", category="opening", title="italian game")
        updated = sm2_next(item, 5, date(2026, 1, 1))
        self.assertEqual(updated.repetitions, 1)
        self.assertEqual(updated.interval, 1)
        self.assertEqual(updated.next_review, date(2026, 1, 2).isoformat())
        self.assertGreaterEqual(updated.ease_factor, 2.5)

    def test_sm2_forgotten_resets(self):
        item = ReviewItem(
            id="x", category="tactic", title="puzzle",
            interval=30, repetitions=5, ease_factor=2.6, next_review="2026-01-01"
        )
        updated = sm2_next(item, 2, date(2026, 1, 1))
        self.assertEqual(updated.repetitions, 1)
        self.assertEqual(updated.interval, 1)
        self.assertEqual(updated.ease_factor, 2.28)

    def test_sm2_quality_bounds(self):
        item = ReviewItem(id="x", category="endgame", title="rook endgame")
        with self.assertRaises(ValueError):
            sm2_next(item, -1, today())
        with self.assertRaises(ValueError):
            sm2_next(item, 6, today())

    def test_sm2_ease_floor(self):
        item = ReviewItem(id="x", category="tactic", title="hard", ease_factor=1.31)
        updated = sm2_next(item, 0, today())
        self.assertEqual(updated.ease_factor, 1.3)

    def test_due_items(self):
        items = [
            ReviewItem(id="a", category="tactic", title="a", next_review="2026-01-01"),
            ReviewItem(id="b", category="tactic", title="b", next_review="2026-02-01"),
        ]
        due = due_items(items, date(2026, 1, 15))
        self.assertEqual([i.id for i in due], ["a"])


class StorageTests(TestCase):
    def setUp(self):
        import tempfile, os
        self.dir = tempfile.mkdtemp()
        self.path = os.path.join(self.dir, "data.json")
        self.storage = Storage(self.path)

    def test_add_and_list(self):
        item = ReviewItem(id="i1", category="tactic", title="queen sac")
        self.storage.add(item)
        items = self.storage.list_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].title, "queen sac")

    def test_grade_advances(self):
        item = ReviewItem(id="i1", category="opening", title="sicilian")
        self.storage.add(item)
        updated = self.storage.grade("i1", 5, on="2026-01-01")
        self.assertEqual(updated.next_review, "2026-01-02")
        self.assertEqual(updated.repetitions, 1)

    def test_grade_missing(self):
        with self.assertRaises(KeyError):
            self.storage.grade("nope", 5)

    def test_export_json_roundtrip(self):
        self.storage.add(ReviewItem(id="i1", category="endgame", title="lucena"))
        self.storage.export_json("/tmp/kilo/export_test.json")
        loaded = self.storage.list_all()
        self.assertEqual(len(loaded), 1)

    def test_export_csv(self):
        self.storage.add(ReviewItem(id="i1", category="tactic", title="t"))
        self.storage.export_csv("/tmp/kilo/export_test.csv")

    def test_import_json(self):
        self.storage.import_json("/tmp/kilo/import_seed.json")

    def test_missing_file_returns_empty(self):
        self.assertEqual(self.storage.list_all(), [])


class CliTests(TestCase):
    def run_cli(self, *args):
        from chess_review.cli import main
        return main(list(args))

    def test_add_then_due(self):
        import tempfile, os
        path = os.path.join(tempfile.mkdtemp(), "data.json")
        self.assertEqual(self.run_cli("--data", path, "add", "--category", "tactic", "--title", "puzzle"), 0)
        self.assertEqual(self.run_cli("--data", path, "due"), 0)
        self.assertEqual(self.run_cli("--data", path, "list"), 0)
        self.assertEqual(self.run_cli("--data", path, "grade", "item-1", "5"), 0)
        self.assertEqual(self.run_cli("--data", path, "review", "item-1"), 0)
        self.assertEqual(self.run_cli("--data", path, "export", "json", "/tmp/kilo/cli_out.json"), 0)
        self.assertEqual(self.run_cli("--data", path, "export", "csv", "/tmp/kilo/cli_out.csv"), 0)

    def test_unknown_id(self):
        import tempfile, os
        path = os.path.join(tempfile.mkdtemp(), "data.json")
        self.assertEqual(self.run_cli("--data", path, "grade", "nope", "5"), 1)
        self.assertEqual(self.run_cli("--data", path, "review", "nope"), 1)
