"""测试命令行入口。"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from dutyrota.cli import main

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "names.txt"


def run_cli(args: list) -> tuple:
    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(args)
    return code, stdout.getvalue(), stderr.getvalue()


class CliTests(unittest.TestCase):
    def test_generates_schedule(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "duty.html"
            code, stdout, _ = run_cli(
                [
                    "-i",
                    str(EXAMPLE),
                    "-o",
                    str(output),
                    "--weeks",
                    "3",
                    "--per-day",
                    "2",
                    "--start",
                    "2026-11-23",
                ]
            )
            self.assertEqual(code, 0)
            content = output.read_text(encoding="utf-8")
            self.assertEqual(content.count('<td><div class="names">'), 15)
            self.assertIn("11/23-11/27", content)
            self.assertIn("已生成", stdout)

    def test_invalid_start_date(self) -> None:
        code, _, stderr = run_cli(["-i", str(EXAMPLE), "--start", "2026/11/23"])
        self.assertEqual(code, 2)
        self.assertIn("YYYY-MM-DD", stderr)

    def test_missing_input(self) -> None:
        code, _, stderr = run_cli(["-i", "/tmp/none.txt"])
        self.assertEqual(code, 2)
        self.assertIn("文件不存在", stderr)

    def test_per_day_too_large(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            names = Path(tmp) / "names.txt"
            names.write_text("张三\n李四\n", encoding="utf-8")
            output = Path(tmp) / "duty.html"
            code, _, stderr = run_cli(
                ["-i", str(names), "-o", str(output), "--per-day", "3"]
            )
            self.assertEqual(code, 2)
            self.assertIn("--per-day", stderr)

    def test_write_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            code, _, stderr = run_cli(["-i", str(EXAMPLE), "-o", tmp])
            self.assertEqual(code, 1)
            self.assertIn("写入文件失败", stderr)

    def test_seed_reproducible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "a.html", Path(tmp) / "b.html"
            run_cli(["-i", str(EXAMPLE), "-o", str(first), "--seed", "7"])
            run_cli(["-i", str(EXAMPLE), "-o", str(second), "--seed", "7"])
            self.assertEqual(
                first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8")
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
