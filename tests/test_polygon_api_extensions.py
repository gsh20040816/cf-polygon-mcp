import unittest
from unittest.mock import Mock, patch

from src.polygon.api.problem_content import save_problem_file
from src.polygon.api.problem_packages import commit_problem_changes
from src.polygon.models import AccessType, FileType
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


if __name__ == "__main__":
    unittest.main()
