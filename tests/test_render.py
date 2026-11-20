"""测试值日表 HTML 输出。"""

from __future__ import annotations

import unittest
from datetime import date

from dutyrota.core import assign
from dutyrota.model import DutyError
from dutyrota.render import render_page

NAMES = ["张伟", "王芳", "李娜", "刘洋", "陈静", "杨帆", "赵敏", "黄磊"]


class RenderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.schedule = assign(NAMES, weeks=2, days=5, per_day=2, seed=1)

    def test_cell_count(self) -> None:
        page = render_page(self.schedule)
        self.assertEqual(page.count('<td><div class="names">'), 2 * 5)

    def test_all_names_rendered(self) -> None:
        page = render_page(self.schedule)
        for name in NAMES:
            self.assertIn(name, page)

    def test_week_labels(self) -> None:
        page = render_page(self.schedule)
        self.assertIn("第 1 周", page)
        self.assertIn("第 2 周", page)

    def test_date_range(self) -> None:
        page = render_page(self.schedule, start=date(2026, 11, 23))
        self.assertIn("11/23-11/27", page)
        self.assertIn("11/30-12/4", page)

    def test_day_headers_with_dates(self) -> None:
        page = render_page(self.schedule, start=date(2026, 11, 23))
        self.assertIn("周一<small>11/23</small>", page)
        self.assertIn("周五<small>11/27</small>", page)

    def test_no_dates_by_default(self) -> None:
        page = render_page(self.schedule)
        self.assertIn("未指定起始日期", page)

    def test_title_escaped(self) -> None:
        page = render_page(self.schedule, title="<i>值日表</i>")
        self.assertNotIn("<i>值日表</i>", page)
        self.assertIn("&lt;i&gt;", page)

    def test_stats_show_counts(self) -> None:
        page = render_page(self.schedule)
        for name, count in self.schedule.loads:
            self.assertIn("%s <b>%d</b> 次" % (name, count), page)

    def test_blank_title_rejected(self) -> None:
        with self.assertRaises(DutyError):
            render_page(self.schedule, title="   ")

    def test_footer_summary(self) -> None:
        page = render_page(self.schedule)
        self.assertIn("共 8 人 · 2 周", page)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
