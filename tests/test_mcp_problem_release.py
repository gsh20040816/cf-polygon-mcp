import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_release import prepare_problem_release
from src.polygon.models import AccessType


def _problem_snapshot(
    revision: int,
    latest_package: int | None,
    modified: bool,
):
    problem = Mock()
    problem.id = 1
    problem.name = "A + B"
    problem.accessType = AccessType.OWNER
    problem.revision = revision
    problem.latestPackage = latest_package
    problem.modified = modified
    return problem


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
        session.problem_id = 1
        session.client.get_problems.side_effect = [
            [_problem_snapshot(revision=10, latest_package=10, modified=True)],
            [_problem_snapshot(revision=11, latest_package=11, modified=False)],
        ]
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": True,
            "blocking_issues": [],
            "warnings": [],
        }
        build_mock.return_value = {"status": "success", "package": {"id": 1, "revision": 11}}

        result = prepare_problem_release(
            problem_id=1,
            testset="tests",
            message="release",
            minor_changes=True,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "prepare_problem_release")
        self.assertEqual(result["stage"], "completed")
        self.assertEqual(result["can_proceed"], True)
        self.assertEqual(
            result["release_options"],
            {
                "testset": "tests",
                "full": True,
                "verify": True,
                "timeout_seconds": 1800,
                "poll_interval_seconds": 5.0,
                "message": "release",
                "minor_changes": True,
                "allow_warnings": False,
                "force": False,
            },
        )
        session.update_working_copy.assert_called_once_with()
        readiness_mock.assert_called_once_with(problem_id=1, pin=None, testset="tests")
        build_mock.assert_called_once()
        session.commit_changes.assert_called_once_with(minor_changes=True, message="release")
        self.assertEqual(result["release_warnings"], [])
        self.assertEqual(result["pre_commit_snapshot"]["revision"], 10)
        self.assertEqual(result["post_commit_snapshot"]["revision"], 11)

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
        self.assertEqual(result["stage"], "readiness")
        self.assertEqual(result["can_proceed"], False)
        self.assertEqual(result["decision"], "blocking_issues")
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
        self.assertEqual(result["stage"], "readiness")
        self.assertEqual(result["decision"], "warnings_not_allowed")
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
        self.assertEqual(result["stage"], "build")
        self.assertEqual(result["can_proceed"], False)
        self.assertEqual(result["decision"], "build_failed")
        session.commit_changes.assert_not_called()

    @patch("src.mcp.utils.problem_release.build_problem_package_and_wait")
    @patch("src.mcp.utils.problem_release.check_problem_readiness")
    @patch("src.mcp.utils.problem_release.get_problem_session")
    def test_prepare_problem_release_reports_post_commit_snapshot_warnings(
        self,
        session_mock,
        readiness_mock,
        build_mock,
    ):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session.commit_changes.return_value = {"status": "OK", "result": {"committed": True}}
        session.problem_id = 1
        session.client.get_problems.side_effect = [
            [_problem_snapshot(revision=10, latest_package=10, modified=True)],
            [_problem_snapshot(revision=12, latest_package=11, modified=True)],
        ]
        session_mock.return_value = session
        readiness_mock.return_value = {
            "ready": True,
            "blocking_issues": [],
            "warnings": [],
        }
        build_mock.return_value = {"status": "success", "package": {"id": 1, "revision": 11}}

        result = prepare_problem_release(problem_id=1)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["stage"], "completed")
        self.assertIn(
            "提交后题目仍处于 modified 状态，可能还有未提交改动",
            result["release_warnings"],
        )
        self.assertIn(
            "构建包 revision=11，提交后题目 revision=12，请确认发布的是预期版本",
            result["release_warnings"],
        )


if __name__ == "__main__":
    unittest.main()
