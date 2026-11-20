"""名单读取与均衡排班算法。"""

from __future__ import annotations

import random
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from .model import DutyError, Schedule

HEADER_NAMES = ("姓名", "名字", "name", "Name", "NAME")
MAX_RETRIES = 50


def normalize_names(raw: Sequence[str]) -> List[str]:
    """清洗名单：去掉空白、忽略空行，并拒绝重名。"""
    names: List[str] = []
    seen = set()
    for item in raw:
        name = item.strip()
        if not name:
            continue
        if name in seen:
            raise DutyError(
                "名单中有重名「%s」，请加区分后缀，例如 %sA / %sB" % (name, name, name)
            )
        seen.add(name)
        names.append(name)
    if not names:
        raise DutyError("名单为空，至少需要一位同学")
    return names


def load_names(path: str) -> List[str]:
    """读取名单。

    支持每行一个名字的 TXT，也支持第一列为姓名的 CSV；
    ``#`` 开头的行视为注释，空行会被跳过。
    """
    source = Path(path)
    if not source.exists():
        raise DutyError("文件不存在: %s" % path)
    if source.is_dir():
        raise DutyError("这是一个目录，需要名单文件: %s" % path)

    try:
        text = source.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise DutyError("无法以 UTF-8 读取 %s，请另存为 UTF-8 编码" % path) from None
    except OSError as exc:
        raise DutyError("读取文件失败: %s" % exc) from exc

    names: List[str] = []
    for line in text.splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        name = entry.split(",")[0].strip()
        if name in HEADER_NAMES:
            continue
        if name:
            names.append(name)

    return normalize_names(names)


def _deal(
    pool: List[str], weeks: int, days: int, per_day: int
) -> Optional[List[List[List[str]]]]:
    """按顺序发牌，保证同一天不出现重复的人；失败时返回 ``None``。"""
    working = list(pool)
    grid: List[List[List[str]]] = []
    for _ in range(weeks):
        week: List[List[str]] = []
        for _ in range(days):
            day: List[str] = []
            for _ in range(per_day):
                picked = next(
                    (index for index, name in enumerate(working) if name not in day),
                    None,
                )
                if picked is None:
                    return None
                day.append(working.pop(picked))
            week.append(day)
        grid.append(week)
    return grid


def assign(
    names: Sequence[str],
    weeks: int = 4,
    days: int = 5,
    per_day: int = 2,
    seed: Optional[int] = None,
) -> Schedule:
    """把名单均衡地排到 ``weeks × days × per_day`` 个岗位上。

    每个人值日次数最多相差 1 次；同一天不会出现重复的人。

    :raises DutyError: 参数越界、名单为空或人数不足以填满每天岗位。
    """
    people = normalize_names(names)
    if not isinstance(weeks, int) or not 1 <= weeks <= 30:
        raise DutyError("周数必须在 1 到 30 之间")
    if not isinstance(days, int) or not 1 <= days <= 7:
        raise DutyError("每周天数必须在 1 到 7 之间")
    if not isinstance(per_day, int) or not 1 <= per_day <= 10:
        raise DutyError("每天人数必须在 1 到 10 之间")
    if per_day > len(people):
        raise DutyError(
            "每天需要 %d 人，但名单只有 %d 人，请增加名单或减少 --per-day"
            % (per_day, len(people))
        )

    rng = random.Random(seed)
    total_slots = weeks * days * per_day
    base, remainder = divmod(total_slots, len(people))

    loads = {name: base for name in people}
    for name in rng.sample(people, remainder):
        loads[name] += 1

    pool = [name for name in people for _ in range(loads[name])]
    for _ in range(MAX_RETRIES):
        rng.shuffle(pool)
        grid = _deal(pool, weeks, days, per_day)
        if grid is not None:
            return Schedule(
                weeks=tuple(tuple(tuple(day) for day in week) for week in grid),
                loads=tuple((name, loads[name]) for name in people),
            )

    raise DutyError("在现有约束下无法完成排班，请增加参与人数或减少每天的岗位数")
