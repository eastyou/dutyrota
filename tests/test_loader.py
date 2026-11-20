"""测试名单文件读取。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from dutyrota.core import load_names
from dutyrota.model import DutyError

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "names.txt"


def write_temp(text: str, encoding: str = "utf-8", suffix: str = ".txt") -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="w", suffix=suffix, delete=False, encoding=encoding
    )
    handle.write(text)
    handle.close()
    return Path(handle.name)


class LoaderTests(unittest.TestCase):
    def test_loads_example(self) -> None:
        names = load_names(str(EXAMPLE))
        self.assertEqual(len(names), 24)
        self.assertEqual(names[0], "张伟")
        self.assertNotIn("#", names)

    def test_csv_first_column(self) -> None:
        source = write_temp("姓名,备注\n张三,班长\n李四,\n", suffix=".csv")
        try:
            self.assertEqual(load_names(str(source)), ["张三", "李四"])
        finally:
            source.unlink()

    def test_csv_without_header(self) -> None:
        source = write_temp("张三,1\n李四,2\n", suffix=".csv")
        try:
            self.assertEqual(load_names(str(source)), ["张三", "李四"])
        finally:
            source.unlink()

    def test_supports_bom(self) -> None:
        source = write_temp("\ufeff张三\n李四\n", encoding="utf-8")
        try:
            self.assertEqual(load_names(str(source)), ["张三", "李四"])
        finally:
            source.unlink()

    def test_skips_comments_and_blanks(self) -> None:
        source = write_temp("# 注释\n\n张三\n   \n李四\n")
        try:
            self.assertEqual(load_names(str(source)), ["张三", "李四"])
        finally:
            source.unlink()

    def test_duplicate_names_rejected(self) -> None:
        source = write_temp("张三\n张三\n")
        try:
            with self.assertRaises(DutyError) as context:
                load_names(str(source))
            self.assertIn("重名", str(context.exception))
        finally:
            source.unlink()

    def test_missing_file(self) -> None:
        with self.assertRaises(DutyError) as context:
            load_names("/tmp/不存在的名单.txt")
        self.assertIn("文件不存在", str(context.exception))

    def test_directory_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(DutyError) as context:
                load_names(tmp)
            self.assertIn("目录", str(context.exception))

    def test_invalid_encoding(self) -> None:
        handle = tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False)
        handle.write(b"\xff\xfe\x00\x00")
        handle.close()
        source = Path(handle.name)
        try:
            with self.assertRaises(DutyError) as context:
                load_names(str(source))
            self.assertIn("UTF-8", str(context.exception))
        finally:
            source.unlink()

    def test_empty_file(self) -> None:
        source = write_temp("# 只有注释\n\n")
        try:
            with self.assertRaises(DutyError) as context:
                load_names(str(source))
            self.assertIn("名单为空", str(context.exception))
        finally:
            source.unlink()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
