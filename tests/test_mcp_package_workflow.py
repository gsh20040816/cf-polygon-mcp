from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_package_workflow import build_problem_package_and_wait
from src.polygon.models import Package, PackageState, PackageType


def _package(package_id: int, state: PackageState) -> Package:
    return Package(
        id=package_id,
        revision=10,
        creationTimeSeconds=datetime(2024, 1, 1, 0, 0, package_id),
        state=state,
        comment="build",
        type=PackageType.STANDARD,
    )


class MpcPackageWorkflowTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_package_workflow.time.sleep")
    @patch("src.mcp.utils.problem_package_workflow.get_problem_session")
    def test_build_problem_package_and_wait_returns_ready_package(self, session_mock, _sleep_mock):
        session = Mock()
        session.get_packages.side_effect = [
            [_package(1, PackageState.READY)],
            [_package(1, PackageState.READY), _package(2, PackageState.PENDING)],
            [_package(1, PackageState.READY), _package(2, PackageState.READY)],
        ]
        session.build_package.return_value = {"ok": True}
        session_mock.return_value = session

        result = build_problem_package_and_wait(
            problem_id=1,
            full=True,
            verify=True,
            timeout_seconds=10,
            poll_interval_seconds=0.01,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["package"]["id"], 2)
        self.assertEqual(result["package"]["state"], "READY")
        session.build_package.assert_called_once_with(full=True, verify=True)

    @patch("src.mcp.utils.problem_package_workflow.time.sleep")
    @patch("src.mcp.utils.problem_package_workflow.get_problem_session")
    def test_build_problem_package_and_wait_returns_failed_package(self, session_mock, _sleep_mock):
        session = Mock()
        session.get_packages.side_effect = [
            [],
            [_package(7, PackageState.RUNNING)],
            [_package(7, PackageState.FAILED)],
        ]
        session.build_package.return_value = {"packageId": 7}
        session_mock.return_value = session

        result = build_problem_package_and_wait(
            problem_id=1,
            full=False,
            verify=False,
            timeout_seconds=10,
            poll_interval_seconds=0.01,
        )

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["package"]["id"], 7)
        self.assertEqual(result["package"]["state"], "FAILED")

    @patch("src.mcp.utils.problem_package_workflow.time.sleep")
    @patch("src.mcp.utils.problem_package_workflow.get_problem_session")
    def test_build_problem_package_and_wait_can_timeout_without_new_package(
        self,
        session_mock,
        _sleep_mock,
    ):
        session = Mock()
        session.get_packages.return_value = [_package(1, PackageState.READY)]
        session.build_package.return_value = {"queued": True}
        session_mock.return_value = session

        with patch(
            "src.mcp.utils.problem_package_workflow.time.monotonic",
            side_effect=[0.0, 0.0, 0.6, 1.2],
        ):
            result = build_problem_package_and_wait(
                problem_id=1,
                full=True,
                verify=False,
                timeout_seconds=1,
                poll_interval_seconds=0.01,
            )

        self.assertEqual(result["status"], "timeout")
        self.assertIsNone(result["package"])


if __name__ == "__main__":
    unittest.main()
