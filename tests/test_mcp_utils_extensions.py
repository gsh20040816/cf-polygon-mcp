from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_content import save_problem_file, save_problem_script
from src.mcp.utils.problem_extra_validators import get_problem_extra_validators
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_sources import save_problem_solution
from src.mcp.utils.problem_tests_extended import save_problem_test_group
from src.polygon.models import FeedbackPolicy, FileType, PointsPolicy, SolutionTag, SourceType


class MpcUtilsExtensionsTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_content.get_problem_session")
    def test_save_problem_file_parses_enum_inputs(self, session_mock):
        session = Mock()
        session.save_file.return_value = {"saved": True}
        session_mock.return_value = session

        result = save_problem_file(
            problem_id=1,
            file_type="resource",
            file_name="testlib.h",
            file_content="content",
            source_type="main",
            stages=["COMPILE"],
            assets=["VALIDATOR"],
        )

        self.assertEqual(result, {"saved": True})
        session.save_file.assert_called_once_with(
            file_type=FileType.RESOURCE,
            name="testlib.h",
            file_content="content",
            source_type=SourceType.MAIN,
            for_types=None,
            stages=["COMPILE"],
            assets=["VALIDATOR"],
            check_existing=None,
        )

    @patch("src.mcp.utils.problem_content.get_problem_session")
    def test_save_problem_file_reads_text_from_local_path(self, session_mock):
        session = Mock()
        session.save_file.return_value = {"saved": True}
        session_mock.return_value = session

        with TemporaryDirectory() as tmpdir:
            local_file = Path(tmpdir) / "checker.cpp"
            local_file.write_text("int main() {}\n", encoding="utf-8")

            result = save_problem_file(
                problem_id=1,
                file_type="source",
                local_path=str(local_file),
                source_type="checker",
            )

        self.assertEqual(result, {"saved": True})
        session.save_file.assert_called_once_with(
            file_type=FileType.SOURCE,
            name="checker.cpp",
            file_content="int main() {}\n",
            source_type=SourceType.CHECKER,
            for_types=None,
            stages=None,
            assets=None,
            check_existing=None,
        )

    @patch("src.mcp.utils.problem_info.get_problem_session")
    def test_get_problem_info_passes_pin(self, session_mock):
        session = Mock()
        session.get_info.return_value = {"id": 1}
        session_mock.return_value = session

        result = get_problem_info(1, pin="4321")

        self.assertEqual(result, {"id": 1})
        session_mock.assert_called_once_with(1, "4321")

    @patch("src.mcp.utils.problem_tests_extended.get_problem_session")
    def test_save_problem_test_group_parses_policy_inputs(self, session_mock):
        session = Mock()
        session.save_test_group.return_value = {"saved": True}
        session_mock.return_value = session

        result = save_problem_test_group(
            problem_id=1,
            testset="tests",
            group="samples",
            points_policy="EACH_TEST",
            feedback_policy="POINTS",
            dependencies=["pretests"],
        )

        self.assertEqual(result, {"saved": True})
        session.save_test_group.assert_called_once_with(
            testset="tests",
            group="samples",
            points_policy=PointsPolicy.EACH_TEST,
            feedback_policy=FeedbackPolicy.POINTS,
            dependencies=["pretests"],
        )

    @patch("src.mcp.utils.problem_extra_validators.get_problem_session")
    def test_get_problem_extra_validators_passes_pin(self, session_mock):
        session = Mock()
        session.get_extra_validators.return_value = ["validator-extra.cpp"]
        session_mock.return_value = session

        result = get_problem_extra_validators(1, pin="5678")

        self.assertEqual(result, ["validator-extra.cpp"])
        session_mock.assert_called_once_with(1, "5678")
        session.get_extra_validators.assert_called_once_with()

    @patch("src.mcp.utils.problem_sources.get_problem_session")
    def test_save_problem_solution_reads_text_from_local_path(self, session_mock):
        session = Mock()
        session.save_solution.return_value = {"saved": True}
        session_mock.return_value = session

        with TemporaryDirectory() as tmpdir:
            local_file = Path(tmpdir) / "main.cpp"
            local_file.write_text("// solution\n", encoding="utf-8")

            result = save_problem_solution(
                problem_id=1,
                local_path=str(local_file),
                source_type="solution",
                tag="MA",
            )

        self.assertEqual(result, {"saved": True})
        session.save_solution.assert_called_once_with(
            name="main.cpp",
            file_content="// solution\n",
            source_type=SourceType.SOLUTION,
            tag=SolutionTag.MA,
            check_existing=None,
        )

    def test_save_problem_script_requires_exactly_one_source_input(self):
        with self.assertRaisesRegex(ValueError, "source 和 local_path 必须且只能提供一个"):
            save_problem_script(
                problem_id=1,
                testset="tests",
                source="gen 1",
                local_path="generator.txt",
            )


if __name__ == "__main__":
    unittest.main()
