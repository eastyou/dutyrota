"""值日轮值表的数据结构与异常定义。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


class DutyError(ValueError):
    """名单或排班参数不合法。"""


@dataclass(frozen=True)
class Schedule:
    """排班结果。

    ``weeks[w][d]`` 表示第 ``w+1`` 周第 ``d+1`` 天值日的同学；
    ``loads`` 按名单顺序保存每个人的值日次数。
    """

    weeks: Tuple[Tuple[Tuple[str, ...], ...], ...]
    loads: Tuple[Tuple[str, int], ...]

    def __post_init__(self) -> None:
        if not self.weeks:
            raise DutyError("排班结果不能为空")
        for week in self.weeks:
            if not week:
                raise DutyError("每周至少需要一天")

    @property
    def week_count(self) -> int:
        return len(self.weeks)

    @property
    def day_count(self) -> int:
        return len(self.weeks[0])

    @property
    def person_count(self) -> int:
        return len(self.loads)

    def load_map(self) -> Dict[str, int]:
        return dict(self.loads)
