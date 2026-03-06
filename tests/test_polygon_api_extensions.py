import unittest
from unittest.mock import Mock, patch

from src.polygon.api.contest_problems import get_contest_problems
from src.polygon.api.problem_content import save_problem_file
from src.polygon.api.problem_extra_validators import get_problem_extra_validators
from src.polygon.api.problem_packages import commit_problem_changes
from src.polygon.api.problem_save_statement import save_problem_statement
from src.polygon.api.problem_sources import save_problem_solution
from src.polygon.api.problem_update_info import update_problem_info
from src.polygon.models import AccessType, FileType, SolutionTag, SourceType
from src.polygon.utils.client_utils import make_api_request


class PolygonApiExtensionsTest(unittest.TestCase):
    @patch("src.polygon.utils.client_utils.requests.request")
    @patch("src.polygon.utils.client_utils.random.randint", return_value=123456)
    @patch("src.polygon.utils.client_utils.time.time", return_value=1700000000)
    def test_make_api_request_uses_post_body(self, _time_mock, _rand_mock, request_mock):
        response = Mock()
        response.json.return_value = {"status": "OK", "result": {"ok": True}}
        response.raise_for_status.return_value = None
        request_mock.return_value = response

        result = make_api_request(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            "problem.saveFile",
            {"name": "main.cpp", "file": "int main() {}"},
            http_method="POST",
        )

        self.assertEqual(result["result"]["ok"], True)
        request_mock.assert_called_once()
        call_args = request_mock.call_args
        self.assertEqual(call_args.args[0], "POST")
        self.assertIn("data", call_args.kwargs)
        self.assertNotIn("params", call_args.kwargs)
        self.assertEqual(call_args.kwargs["timeout"], 30)

    def test_save_problem_file_requires_complete_resource_properties(self):
        with self.assertRaisesRegex(ValueError, "需要同时提供"):
            save_problem_file(
                "key",
                "secret",
                "https://polygon.codeforces.com/api/",
                1,
                AccessType.OWNER,
                FileType.RESOURCE,
                "testlib.h",
                "content",
                for_types="cpp.g++17",
            )

    @patch("src.polygon.api.problem_content.make_problem_request", return_value={"status": "OK", "result": {"saved": True}})
    def test_save_problem_file_serializes_resource_properties(self, request_mock):
        result = save_problem_file(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            AccessType.OWNER,
            FileType.RESOURCE,
            "testlib.h",
            "content",
            for_types="cpp.g++17",
            stages=["COMPILE", "RUN"],
            assets=["VALIDATOR", "CHECKER"],
            check_existing=True,
        )

        self.assertEqual(result, {"saved": True})
        args, kwargs = request_mock.call_args
        self.assertEqual(kwargs["http_method"], "POST")
        self.assertEqual(args[6]["stages"], "COMPILE;RUN")
        self.assertEqual(args[6]["assets"], "VALIDATOR;CHECKER")
        self.assertEqual(args[6]["checkExisting"], "true")

    @patch("src.polygon.api.problem_packages.make_problem_request", return_value={"status": "OK", "result": {"committed": True}})
    def test_commit_problem_changes_passes_optional_fields(self, request_mock):
        result = commit_problem_changes(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            AccessType.OWNER,
            message="sync docs",
            minor_changes=True,
        )

        self.assertEqual(result, {"committed": True})
        args, _ = request_mock.call_args
        self.assertEqual(args[6]["minorChanges"], "true")
        self.assertEqual(args[6]["message"], "sync docs")

    @patch(
        "src.polygon.api.problem_sources.make_problem_request",
        return_value={"status": "OK", "result": {"saved": True}},
    )
    def test_save_problem_solution_omits_source_type_parameter(self, request_mock):
        result = save_problem_solution(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            AccessType.OWNER,
            "wa.cpp",
            "int main() {}",
            source_type=SourceType.SOLUTION,
            tag=SolutionTag.WA,
            check_existing=True,
        )

        self.assertEqual(result, {"saved": True})
        args, kwargs = request_mock.call_args
        self.assertEqual(kwargs["http_method"], "POST")
        self.assertNotIn("sourceType", args[6])
        self.assertEqual(args[6]["tag"], "WA")
        self.assertEqual(args[6]["checkExisting"], "true")

    def test_save_problem_solution_rejects_non_solution_source_type(self):
        with self.assertRaisesRegex(ValueError, "只接受 solution 类型"):
            save_problem_solution(
                "key",
                "secret",
                "https://polygon.codeforces.com/api/",
                1,
                AccessType.OWNER,
                "wa.cpp",
                "int main() {}",
                source_type=SourceType.CHECKER,
            )

    @patch(
        "src.polygon.api.problem_extra_validators.make_problem_request",
        return_value={"status": "OK", "result": ["validator-a.cpp", "validator-b.cpp"]},
    )
    def test_get_problem_extra_validators_returns_validator_names(self, request_mock):
        result = get_problem_extra_validators(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            pin="9999",
        )

        self.assertEqual(result, ["validator-a.cpp", "validator-b.cpp"])
        request_mock.assert_called_once_with(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            "problem.extraValidators",
            1,
            "9999",
        )

    @patch(
        "src.polygon.api.problem_update_info.make_problem_request",
        return_value={"status": "OK", "result": {"updated": True}},
    )
    def test_update_problem_info_uses_post(self, request_mock):
        result = update_problem_info(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            None,
            AccessType.OWNER,
            input_file="stdin",
            output_file="stdout",
            interactive=False,
        )

        self.assertEqual(result, {"status": "OK", "result": {"updated": True}})
        args, kwargs = request_mock.call_args
        self.assertEqual(args[3], "problem.updateInfo")
        self.assertEqual(args[6]["inputFile"], "stdin")
        self.assertEqual(args[6]["outputFile"], "stdout")
        self.assertEqual(args[6]["interactive"], "false")
        self.assertEqual(kwargs["http_method"], "POST")

    @patch("builtins.print")
    @patch(
        "src.polygon.api.problem_save_statement.make_problem_request",
        return_value={"status": "OK", "result": {"saved": True}},
    )
    def test_save_problem_statement_uses_post_and_does_not_print(
        self,
        request_mock,
        print_mock,
    ):
        result = save_problem_statement(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            1,
            "english",
            AccessType.OWNER,
            name="A + B",
            legend="desc",
        )

        self.assertEqual(result, {"saved": True})
        args, kwargs = request_mock.call_args
        self.assertEqual(args[3], "problem.saveStatement")
        self.assertEqual(kwargs["http_method"], "POST")
        print_mock.assert_not_called()

    @patch("builtins.print")
    @patch(
        "src.polygon.api.contest_problems.make_contest_request",
        return_value={
            "status": "OK",
            "result": {
                "B": {
                    "id": 2,
                    "name": "Beta",
                    "owner": "owner",
                    "accessType": "WRITE",
                },
                "A": {
                    "id": 1,
                    "name": "Alpha",
                    "owner": "owner",
                    "accessType": "OWNER",
                },
            },
        },
    )
    def test_get_contest_problems_parses_letter_mapping_without_printing(
        self,
        request_mock,
        print_mock,
    ):
        problems = get_contest_problems(
            "key",
            "secret",
            "https://polygon.codeforces.com/api/",
            123,
        )

        self.assertEqual([problem.contestLetter for problem in problems], ["A", "B"])
        self.assertEqual([problem.name for problem in problems], ["Alpha", "Beta"])
        request_mock.assert_called_once()
        print_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
