from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.contest_problems import get_contest_problems
from src.mcp.utils.problem_content import save_problem_file, save_problem_script
from src.mcp.utils.problem_extra_validators import get_problem_extra_validators
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_save_statement import save_problem_statement
from src.mcp.utils.problem_sources import save_problem_solution
from src.mcp.utils.problem_tests_extended import save_problem_test_group
from src.mcp.utils.problem_update_info import update_problem_info
from src.mcp.utils.problem_working_copy import (
    discard_problem_working_copy,
    update_problem_working_copy,
)
from src.polygon.models import (
    AccessType,
    FeedbackPolicy,
    FileType,
    PointsPolicy,
    Problem,
    ProblemInfo,
    Statement,
    SolutionTag,
    SourceType,
)


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
            source_type=None,
            tag=SolutionTag.MA,
            check_existing=None,
        )

    def test_save_problem_solution_rejects_non_solution_source_type(self):
        with self.assertRaisesRegex(ValueError, "只支持 solution 类型"):
            save_problem_solution(
                problem_id=1,
                name="wa.cpp",
                file_content="int main() {}",
                source_type="checker",
                tag="WA",
            )

    def test_save_problem_script_requires_exactly_one_source_input(self):
        with self.assertRaisesRegex(ValueError, "source 和 local_path 必须且只能提供一个"):
            save_problem_script(
                problem_id=1,
                testset="tests",
                source="gen 1",
                local_path="generator.txt",
            )

    @patch("src.mcp.utils.problem_save_statement.get_client")
    def test_save_problem_statement_returns_statement_snapshot(self, get_client_mock):
        statement = Statement(
            encoding="UTF-8",
            name="A + B",
            legend="desc",
            input="in",
            output="out",
        )
        statements = Mock()
        statements.get.return_value = statement
        session = Mock()
        session.save_statement.return_value = {"saved": True}
        session.get_statements.return_value = statements
        client = Mock()
        client.create_problem_session.return_value = session
        get_client_mock.return_value = client

        result = save_problem_statement(
            problem_id=1,
            lang="english",
            name="A + B",
            legend="desc",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "save_problem_statement")
        self.assertEqual(result["problem_id"], 1)
        self.assertEqual(result["lang"], "english")
        self.assertEqual(result["requested_fields"], ["legend", "name"])
        self.assertEqual(result["result"], {"saved": True})
        self.assertEqual(result["statement"]["name"], "A + B")
        session.get_statements.assert_called_once_with()

    @patch("src.mcp.utils.problem_update_info.get_problem_session")
    def test_update_problem_info_returns_updated_snapshot(self, session_mock):
        session = Mock()
        session.update_info.return_value = {"status": "OK", "result": {"updated": True}}
        session.get_info.return_value = ProblemInfo(
            inputFile="stdin",
            outputFile="stdout",
            interactive=False,
            timeLimit=2000,
            memoryLimit=256,
        )
        session_mock.return_value = session

        result = update_problem_info(
            problem_id=1,
            input_file="stdin",
            output_file="stdout",
            time_limit=2000,
            memory_limit=256,
            interactive=False,
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "update_problem_info")
        self.assertEqual(
            result["requested_changes"],
            {
                "input_file": "stdin",
                "output_file": "stdout",
                "time_limit": 2000,
                "memory_limit": 256,
                "interactive": False,
            },
        )
        self.assertEqual(result["problem_info"]["time_limit"], 2000)
        self.assertEqual(result["result"], {"status": "OK", "result": {"updated": True}})
        session.get_info.assert_called_once_with()

    @patch("src.mcp.utils.problem_working_copy.get_problem_session")
    def test_update_problem_working_copy_returns_problem_snapshot(self, session_mock):
        session = Mock()
        session.update_working_copy.return_value = {"status": "OK"}
        session.client.get_problems.return_value = [
            Problem(
                id=1,
                owner="owner",
                name="A + B",
                accessType=AccessType.OWNER,
                revision=5,
                latestPackage=4,
                modified=True,
            )
        ]
        session_mock.return_value = session

        result = update_problem_working_copy(problem_id=1, pin="1234")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "update_problem_working_copy")
        self.assertEqual(result["problem"]["revision"], 5)
        self.assertEqual(result["pin"], "1234")
        session.client.get_problems.assert_called_once_with(problem_id=1)

    @patch("src.mcp.utils.problem_working_copy.get_problem_session")
    def test_discard_problem_working_copy_returns_problem_snapshot(self, session_mock):
        session = Mock()
        session.discard_working_copy.return_value = {"status": "OK"}
        session.client.get_problems.return_value = [
            Problem(
                id=1,
                owner="owner",
                name="A + B",
                accessType=AccessType.WRITE,
                revision=6,
                latestPackage=6,
                modified=False,
            )
        ]
        session_mock.return_value = session

        result = discard_problem_working_copy(problem_id=1)

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "discard_problem_working_copy")
        self.assertEqual(result["problem"]["modified"], False)
        self.assertEqual(result["result"], {"status": "OK"})

    @patch("builtins.print")
    @patch("src.mcp.utils.contest_problems.PolygonClient")
    @patch("src.mcp.utils.contest_problems.get_api_credentials", return_value=("key", "secret"))
    def test_get_contest_problems_is_silent(self, _credentials_mock, client_cls, print_mock):
        problems = [
            Problem(
                id=1,
                owner="owner",
                name="A",
                accessType=AccessType.OWNER,
                contestLetter="A",
            )
        ]
        session = Mock()
        session.get_problems.return_value = problems
        client = Mock()
        client.create_contest_session.return_value = session
        client_cls.return_value = client

        result = get_contest_problems(contest_id=1000, pin="9999")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["contest_id"], 1000)
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["letters"], ["A"])
        self.assertEqual(result["problem_summaries"][0]["name"], "A")
        self.assertEqual(result["problem_summaries"][0]["contest_letter"], "A")
        self.assertEqual(result["problems"], problems)
        client.create_contest_session.assert_called_once_with(1000, "9999")
        print_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
