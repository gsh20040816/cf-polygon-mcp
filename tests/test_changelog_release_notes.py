from pathlib import Path
import tomllib
import unittest


class ChangelogReleaseNotesTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.pyproject = tomllib.loads((self.root / "pyproject.toml").read_text(encoding="utf-8"))
        self.changelog = (self.root / "CHANGELOG.md").read_text(encoding="utf-8")
        self.publish_workflow = (
            self.root / ".github" / "workflows" / "publish.yml"
        ).read_text(encoding="utf-8")

    def test_changelog_contains_unreleased_section(self):
        self.assertIn("# Changelog", self.changelog)
        self.assertIn("## [Unreleased]", self.changelog)

    def test_current_version_has_release_notes(self):
        version = self.pyproject["project"]["version"]
        version_heading = f"## [{version}]"

        self.assertIn(version_heading, self.changelog)

        version_section = self.changelog.split(version_heading, maxsplit=1)[1]
        next_section = version_section.split("\n## [", maxsplit=1)[0]

        self.assertIn("- ", next_section)
        self.assertTrue(
            any(
                subsection in next_section
                for subsection in ("### Added", "### Changed", "### Fixed")
            )
        )

    def test_publish_workflow_checks_changelog_before_pypi_publish(self):
        self.assertIn('Path("CHANGELOG.md")', self.publish_workflow)
        self.assertIn('version_heading = f"## [{version}]"', self.publish_workflow)
        self.assertIn("## [Unreleased]", self.publish_workflow)
        self.assertIn("CHANGELOG.md does not contain a release note section", self.publish_workflow)


if __name__ == "__main__":
    unittest.main()
