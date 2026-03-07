from pathlib import Path
import tomllib
import unittest

from setuptools import find_packages


class PackagingConfigTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.pyproject = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))

    def read_workflow(self, name: str) -> str:
        return (self.root / ".github" / "workflows" / name).read_text(encoding="utf-8")

    def test_find_packages_discovers_all_src_packages(self):
        expected_packages = sorted(
            ".".join(package_init.parent.relative_to(self.root).parts)
            for package_init in self.root.joinpath("src").rglob("__init__.py")
            if "__pycache__" not in package_init.parts
        )

        discovered_packages = sorted(find_packages(where=".", include=["src*"]))

        self.assertEqual(discovered_packages, expected_packages)

    def test_pyproject_uses_auto_package_discovery(self):
        setuptools_config = self.pyproject["tool"]["setuptools"]
        package_discovery = setuptools_config["packages"]["find"]

        self.assertNotIsInstance(setuptools_config.get("packages"), list)
        self.assertEqual(package_discovery["where"], ["."])
        self.assertEqual(package_discovery["include"], ["src*"])
        self.assertIs(package_discovery["namespaces"], False)

    def test_project_requires_python_311(self):
        self.assertEqual(self.pyproject["project"]["requires-python"], ">=3.11")

    def test_ci_workflow_runs_on_main_and_pull_requests(self):
        workflow_text = self.read_workflow("ci.yml")

        self.assertIn('python-version: "3.11"', workflow_text)
        self.assertIn("python -m pip install --upgrade pip build setuptools", workflow_text)
        self.assertIn("push:", workflow_text)
        self.assertIn("branches:", workflow_text)
        self.assertIn("- main", workflow_text)
        self.assertIn("pull_request:", workflow_text)
        self.assertIn("python -m unittest discover -s tests -v", workflow_text)
        self.assertIn("python -m build", workflow_text)

    def test_publish_workflow_requires_version_tag(self):
        workflow_text = self.read_workflow("publish.yml")

        self.assertIn('python-version: "3.11"', workflow_text)
        self.assertIn("python -m pip install --upgrade pip build setuptools", workflow_text)
        self.assertIn("tags:", workflow_text)
        self.assertIn('- "v*"', workflow_text)
        self.assertNotIn("branches:\n      - main", workflow_text)
        self.assertIn('expected_tag = f"v{version}"', workflow_text)
        self.assertIn("if tag != expected_tag:", workflow_text)


if __name__ == "__main__":
    unittest.main()
