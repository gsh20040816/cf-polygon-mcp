import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_release import prepare_problem_release


class MpcProblemReleaseTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_release.build_problem_package_and_wait")
    @patch("src.mcp.utils.problem_release.check_problem_readiness")
    @patch("src.mcp.utils.problem_release.get_problem_session")
    def test_prepare_problem_release_runs_full_flow(
        self,
        session_mock,
        readiness_mock,
        build_mock,
    ):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session.commit_changes.return_value = {"status": "OK", "result": {"committed": True}}
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": True,
            "blocking_issues": [],
            "warnings": [],
        }
        build_mock.return_value = {"status": "success", "package": {"id": 1}}

        result = prepare_problem_release(
            problem_id=1,
            testset="tests",
            message="release",
            minor_changes=True,
        )

        self.assertEqual(result["status"], "success")
        session.update_working_copy.assert_called_once_with()
        readiness_mock.assert_called_once_with(problem_id=1, pin=None, testset="tests")
        build_mock.assert_called_once()
        session.commit_changes.assert_called_once_with(minor_changes=True, message="release")

    @patch("src.mcp.utils.problem_release.build_problem_package_and_wait")
    @patch("src.mcp.utils.problem_release.check_problem_readiness")
    @patch("src.mcp.utils.problem_release.get_problem_session")
    def test_prepare_problem_release_blocks_on_readiness_issues(
        self,
        session_mock,
        readiness_mock,
        build_mock,
    ):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": False,
            "blocking_issues": ["缺少题面"],
            "warnings": [],
        }

        result = prepare_problem_release(problem_id=1)

        self.assertEqual(result["status"], "blocked")
        build_mock.assert_not_called()
        session.commit_changes.assert_not_called()

    @patch("src.mcp.utils.problem_release.build_problem_package_and_wait")
    @patch("src.mcp.utils.problem_release.check_problem_readiness")
    @patch("src.mcp.utils.problem_release.get_problem_session")
    def test_prepare_problem_release_blocks_on_warnings_without_allowing_them(
        self,
        session_mock,
        readiness_mock,
        build_mock,
    ):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": True,
            "blocking_issues": [],
            "warnings": ["还没有 READY 状态的题目包"],
        }

        result = prepare_problem_release(problem_id=1)

        self.assertEqual(result["status"], "blocked")
        build_mock.assert_not_called()
        session.commit_changes.assert_not_called()

    @patch("src.mcp.utils.problem_release.build_problem_package_and_wait")
    @patch("src.mcp.utils.problem_release.check_problem_readiness")
    @patch("src.mcp.utils.problem_release.get_problem_session")
    def test_prepare_problem_release_does_not_commit_after_build_failure(
        self,
        session_mock,
        readiness_mock,
        build_mock,
    ):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": True,
            "blocking_issues": [],
            "warnings": [],
        }
        build_mock.return_value = {"status": "error", "message": "failed"}

        result = prepare_problem_release(problem_id=1)

        self.assertEqual(result["status"], "error")
        session.commit_changes.assert_not_called()


if __name__ == "__main__":
    unittest.main()
