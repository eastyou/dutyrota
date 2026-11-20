"""测试名单清洗与均衡排班算法。"""

from __future__ import annotations

import unittest

from dutyrota.core import assign, normalize_names
from dutyrota.model import DutyError, Schedule

NAMES = ["张伟", "王芳", "李娜", "刘洋", "陈静", "杨帆"]


class NormalizeTests(unittest.TestCase):
    def test_strips_and_skips_blank(self) -> None:
        self.assertEqual(normalize_names([" 张三 ", "", "李四"]), ["张三", "李四"])

    def test_duplicate_rejected(self) -> None:
        with self.assertRaises(DutyError) as context:
            normalize_names(["张伟", "张伟"])
        self.assertIn("重名", str(context.exception))

    def test_empty_rejected(self) -> None:
        with self.assertRaises(DutyError):
            normalize_names(["", "  "])


class AssignTests(unittest.TestCase):
    def test_total_slots(self) -> None:
        schedule = assign(NAMES, weeks=3, days=5, per_day=2, seed=1)
        total = sum(
            len(day) for week in schedule.weeks for day in week
        )
        self.assertEqual(total, 3 * 5 * 2)

    def test_loads_are_balanced(self) -> None:
        schedule = assign(NAMES, weeks=4, days=5, per_day=2, seed=2)
        counts = [count for _, count in schedule.loads]
        self.assertLessEqual(max(counts) - min(counts), 1)

    def test_loads_match_cells(self) -> None:
        schedule = assign(NAMES, weeks=4, days=5, per_day=2, seed=3)
        actual = {name: 0 for name in NAMES}
        for week in schedule.weeks:
            for day in week:
                for name in day:
                    actual[name] += 1
        self.assertEqual(actual, schedule.load_map())

    def test_no_duplicate_within_day(self) -> None:
        schedule = assign(NAMES, weeks=4, days=5, per_day=3, seed=4)
        for week in schedule.weeks:
            for day in week:
                self.assertEqual(len(day), len(set(day)))

    def test_seed_reproducible(self) -> None:
        first = assign(NAMES, weeks=2, days=5, per_day=2, seed=9)
        second = assign(NAMES, weeks=2, days=5, per_day=2, seed=9)
        self.assertEqual(first, second)

    def test_different_seeds_differ(self) -> None:
        first = assign(NAMES, weeks=3, days=5, per_day=2, seed=1)
        second = assign(NAMES, weeks=3, days=5, per_day=2, seed=2)
        self.assertNotEqual(first.weeks, second.weeks)

    def test_people_larger_than_slots(self) -> None:
        schedule = assign(NAMES, weeks=1, days=1, per_day=1, seed=5)
        counts = [count for _, count in schedule.loads]
        self.assertEqual(sum(counts), 1)
        self.assertEqual(max(counts), 1)

    def test_input_list_not_mutated(self) -> None:
        original = list(NAMES)
        assign(NAMES, weeks=2, days=5, per_day=2, seed=6)
        self.assertEqual(NAMES, original)

    def test_per_day_exceeds_people(self) -> None:
        with self.assertRaises(DutyError) as context:
            assign(["A", "B"], weeks=1, days=1, per_day=3)
        self.assertIn("--per-day", str(context.exception))

    def test_invalid_weeks(self) -> None:
        for weeks in (0, 31):
            with self.assertRaises(DutyError):
                assign(NAMES, weeks=weeks)

    def test_invalid_days(self) -> None:
        for days in (0, 8):
            with self.assertRaises(DutyError):
                assign(NAMES, days=days)

    def test_invalid_per_day(self) -> None:
        for per_day in (0, 11):
            with self.assertRaises(DutyError):
                assign(NAMES, per_day=per_day)

    def test_schedule_properties(self) -> None:
        schedule = assign(NAMES, weeks=3, days=5, per_day=2, seed=7)
        self.assertEqual(schedule.week_count, 3)
        self.assertEqual(schedule.day_count, 5)
        self.assertEqual(schedule.person_count, len(NAMES))

    def test_empty_schedule_rejected(self) -> None:
        with self.assertRaises(DutyError):
            Schedule(weeks=(), loads=())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
