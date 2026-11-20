"""支持 ``python -m dutyrota``。"""

from .cli import main

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
