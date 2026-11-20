"""把排班结果渲染成可打印的 A4 值日轮值表。"""

from __future__ import annotations

import html
from datetime import date, timedelta
from typing import List, Optional

from .model import DutyError, Schedule

WEEKDAYS = ("周一", "周二", "周三", "周四", "周五", "周六", "周日")

PAGE_TEMPLATE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 20px 24px 26px;
    background: #f8fafc;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  header {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    border-bottom: 2px solid #0f172a;
    padding-bottom: 10px;
    margin-bottom: 14px;
  }
  h1 { font-size: 21px; margin: 0; letter-spacing: 1px; }
  .meta { color: #64748b; font-size: 12px; margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; table-layout: fixed; }
  thead { display: table-header-group; }
  th, td {
    border: 1px solid #cbd5e1;
    padding: 7px 6px;
    text-align: center;
    vertical-align: middle;
    font-size: 12px;
  }
  th {
    background: #f1f5f9;
    color: #334155;
    font-weight: 600;
  }
  th small { display: block; color: #94a3b8; font-weight: 400; font-size: 10px; }
  td { background: #fff; }
  td .names {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 3px 8px;
    line-height: 1.5;
  }
  td .names span {
    background: #eff6ff;
    color: #1d4ed8;
    border-radius: 5px;
    padding: 1px 7px;
    font-size: 11px;
    white-space: nowrap;
  }
  .week {
    background: #f8fafc;
    color: #475569;
    font-weight: 600;
    white-space: nowrap;
  }
  .week small { display: block; color: #94a3b8; font-weight: 400; font-size: 10px; }
  .stats {
    margin-top: 16px;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 12px 14px;
    background: #fff;
  }
  .stats h2 {
    font-size: 13px;
    margin: 0 0 8px;
    color: #334155;
    letter-spacing: 0.5px;
  }
  .stat-list { display: flex; flex-wrap: wrap; gap: 6px 10px; }
  .stat {
    border: 1px solid #e2e8f0;
    border-radius: 999px;
    padding: 3px 10px;
    font-size: 11px;
    color: #334155;
    background: #f8fafc;
  }
  .stat b { color: #1d4ed8; }
  footer {
    margin-top: 14px;
    color: #94a3b8;
    font-size: 11px;
    display: flex;
    justify-content: space-between;
  }
  @page { size: A4 portrait; margin: 10mm; }
  @media print {
    body { background: #fff; padding: 0; }
    tr, .stats { break-inside: avoid; }
    td .names span { border: 1px solid #dbeafe; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
</style>
</head>
<body>
<header>
  <div>
    <h1>__TITLE__</h1>
    <div class="meta">__META__</div>
  </div>
</header>
<table>
  <thead>
    <tr><th style="width:88px">周次</th>__HEADERS__</tr>
  </thead>
  <tbody>
__ROWS__
  </tbody>
</table>
<div class="stats">
  <h2>值日次数统计（次数最多相差 1 次）</h2>
  <div class="stat-list">__STATS__</div>
</div>
<footer>
  <span>dutyrota · 共 __PEOPLE__ 人 · __WEEKS__ 周</span>
  <span>A4 纵向打印，建议缩放 100%</span>
</footer>
</body>
</html>
"""


def _week_range(start: date, week_index: int, days: int) -> str:
    begin = start + timedelta(days=7 * week_index)
    end = begin + timedelta(days=days - 1)
    return "%d/%d-%d/%d" % (begin.month, begin.day, end.month, end.day)


def render_page(
    schedule: Schedule,
    title: str = "班级值日表",
    start: Optional[date] = None,
) -> str:
    """生成整页 HTML；标题为空时抛出 ``DutyError``。"""
    if not title.strip():
        raise DutyError("标题不能为空")
    days = schedule.day_count
    if days > len(WEEKDAYS):
        raise DutyError("每周天数不能超过 7 天")

    headers: List[str] = []
    for index in range(days):
        extra = ""
        if start is not None:
            current = start + timedelta(days=index)
            extra = "<small>%d/%d</small>" % (current.month, current.day)
        headers.append("<th>%s%s</th>" % (WEEKDAYS[index], extra))

    rows: List[str] = []
    for week_index, week in enumerate(schedule.weeks):
        label = "第 %d 周" % (week_index + 1)
        small = ""
        if start is not None:
            small = "<small>%s</small>" % _week_range(start, week_index, days)
        cells = []
        for day in week:
            names = "".join("<span>%s</span>" % html.escape(name) for name in day)
            cells.append('<td><div class="names">%s</div></td>' % names)
        rows.append(
            '<tr><td class="week">%s%s</td>%s</tr>' % (label, small, "".join(cells))
        )

    stats = "".join(
        '<span class="stat">%s <b>%d</b> 次</span>' % (html.escape(name), count)
        for name, count in schedule.loads
    )

    date_note = "从 %s 起" % start.isoformat() if start is not None else "未指定起始日期"
    meta = "%d 周 · 每周 %d 天 · 每天 %d 人 · %s" % (
        schedule.week_count,
        days,
        len(schedule.weeks[0][0]),
        date_note,
    )

    page = PAGE_TEMPLATE
    replacements = {
        "__TITLE__": html.escape(title.strip()),
        "__META__": html.escape(meta),
        "__HEADERS__": "".join(headers),
        "__ROWS__": "\n".join(rows),
        "__STATS__": stats,
        "__PEOPLE__": str(schedule.person_count),
        "__WEEKS__": str(schedule.week_count),
    }
    for key, value in replacements.items():
        page = page.replace(key, value)
    return page
