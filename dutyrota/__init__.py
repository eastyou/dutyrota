"""dutyrota：零依赖的值日轮值表生成器。"""

from .core import assign, load_names, normalize_names
from .model import DutyError, Schedule
from .render import render_page

__version__ = "0.1.0"

__all__ = [
    "DutyError",
    "Schedule",
    "assign",
    "load_names",
    "normalize_names",
    "render_page",
    "__version__",
]
