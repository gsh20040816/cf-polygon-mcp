import ast
from pathlib import Path
import unittest


class PythonCompatibilityTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]

    def test_source_and_tests_parse_under_python_311(self):
        checked_files: list[Path] = []

        for top_level in ("src", "tests"):
            for path in sorted((self.root / top_level).rglob("*.py")):
                if "__pycache__" in path.parts:
                    continue

                source = path.read_text(encoding="utf-8")
                try:
                    ast.parse(source, filename=str(path), feature_version=(3, 11))
                except SyntaxError as exc:
                    self.fail(f"{path} 不能按 Python 3.11 语法解析: {exc}")

                checked_files.append(path)

        self.assertTrue(checked_files)


if __name__ == "__main__":
    unittest.main()
