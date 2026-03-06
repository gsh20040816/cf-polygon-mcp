import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_content import save_problem_file
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_tests_extended import save_problem_test_group
from src.polygon.models import FeedbackPolicy, FileType, PointsPolicy, SourceType


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


if __name__ == "__main__":
    unittest.main()
