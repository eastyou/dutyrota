"""命令行入口：生成可打印的值日轮值表。"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Optional, Sequence

from .core import assign, load_names
from .model import DutyError
from .render import render_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dutyrota",
        description="值日轮值表生成器：名单均衡轮转，输出可打印的 A4 值日表",
    )
    parser.add_argument("--version", action="version", version="dutyrota 0.1.0")
    parser.add_argument("-i", "--input", required=True, help="名单文件（TXT 或 CSV）")
    parser.add_argument("-o", "--output", default="值日表.html", help="输出 HTML 路径")
    parser.add_argument("--title", default="班级值日表", help="值日表标题")
    parser.add_argument("--weeks", type=int, default=4, help="排几周，1~30，默认 4")
    parser.add_argument("--days", type=int, default=5, help="每周几天，1~7，默认 5")
    parser.add_argument(
        "--per-day", type=int, default=2, help="每天几个人，1~10，默认 2"
    )
    parser.add_argument(
        "--start", default=None, help="起始日期，如 2026-11-23（默认不显示日期）"
    )
    parser.add_argument("--seed", type=int, default=None, help="随机种子，便于复现")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        start = None
        if args.start:
            try:
                start = date.fromisoformat(args.start)
            except ValueError:
                raise DutyError(
                    "--start 日期格式应为 YYYY-MM-DD，例如 2026-11-23"
                ) from None

        names = load_names(args.input)
        schedule = assign(
            names,
            weeks=args.weeks,
            days=args.days,
            per_day=args.per_day,
            seed=args.seed,
        )
        page = render_page(schedule, title=args.title, start=start)
    except DutyError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    print(
        "已生成 %s：%d 人，%d 周，每周 %d 天，每天 %d 人"
        % (args.output, len(names), schedule.week_count, args.days, args.per_day)
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
