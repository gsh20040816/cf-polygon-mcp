import importlib
import inspect
import unittest
from pathlib import Path

from src.mcp.server import register_tools
from src.mcp.tool_registry import get_registered_tool_names, validate_tool_registry


class _FakeMCP:
    def __init__(self):
        self.registered_names: list[str] = []

    def tool(self):
        def decorator(func):
            self.registered_names.append(func.__name__)
            return func

        return decorator


class MpcServerRegistryTest(unittest.TestCase):
    def test_register_tools_uses_registry_order(self):
        fake_mcp = _FakeMCP()

        returned_names = register_tools(fake_mcp)

        self.assertEqual(returned_names, get_registered_tool_names())
        self.assertEqual(fake_mcp.registered_names, get_registered_tool_names())

    def test_tool_registry_covers_all_public_utils_functions(self):
        utils_dir = Path(__file__).resolve().parents[1] / "src" / "mcp" / "utils"
        discovered_names: set[str] = set()

        for module_path in sorted(utils_dir.glob("*.py")):
            if module_path.name in {"__init__.py", "common.py"}:
                continue
            module = importlib.import_module(f"src.mcp.utils.{module_path.stem}")
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if func.__module__ != module.__name__:
                    continue
                if name.startswith("_"):
                    continue
                discovered_names.add(name)

        registered_names = set(get_registered_tool_names())
        self.assertEqual(
            discovered_names,
            registered_names,
            msg=(
                "工具注册表与 utils 公开函数不一致: "
                f"missing={sorted(discovered_names - registered_names)}, "
                f"extra={sorted(registered_names - discovered_names)}"
            ),
        )

    def test_validate_tool_registry_passes_for_current_registry(self):
        validate_tool_registry()


if __name__ == "__main__":
    unittest.main()
