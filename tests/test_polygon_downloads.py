import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.downloads import download_problem_package_by_url
from src.polygon.download import (
    download_contest_descriptor,
    download_contest_statements_pdf,
    download_problem_descriptor,
)


class PolygonDownloadsTest(unittest.TestCase):
    @patch("src.polygon.download.requests.post")
    def test_download_problem_descriptor_builds_problem_xml_url(self, post_mock):
        response = Mock()
        response.content = b"<problem />"
        response.raise_for_status.return_value = None
        post_mock.return_value = response

        content = download_problem_descriptor(
            "https://polygon.codeforces.com/p/demo/a-plus-b",
            "login",
            "password",
            revision=12,
        )

        self.assertEqual(content, b"<problem />")
        post_mock.assert_called_once_with(
            "https://polygon.codeforces.com/p/demo/a-plus-b/problem.xml",
            data={"login": "login", "password": "password", "revision": "12"},
            timeout=30,
        )

    @patch("src.polygon.download.requests.post")
    def test_download_contest_helpers_append_suffixes(self, post_mock):
        response = Mock()
        response.content = b"ok"
        response.raise_for_status.return_value = None
        post_mock.return_value = response

        download_contest_descriptor("https://polygon.codeforces.com/c/contest-uid", "login", "password")
        download_contest_statements_pdf(
            "https://polygon.codeforces.com/c/contest-uid",
            "login",
            "password",
            language="english",
        )

        self.assertEqual(post_mock.call_count, 2)
        self.assertEqual(
            post_mock.call_args_list[0].args[0],
            "https://polygon.codeforces.com/c/contest-uid/contest.xml",
        )
        self.assertEqual(
            post_mock.call_args_list[1].args[0],
            "https://polygon.codeforces.com/c/contest-uid/english/statements.pdf",
        )

    @patch("src.mcp.utils.downloads.get_account_credentials", return_value=("env-login", "env-password"))
    @patch("src.mcp.utils.downloads._download_problem_package", return_value=b"zip")
    def test_mcp_download_problem_package_uses_account_credentials(self, download_mock, creds_mock):
        content = download_problem_package_by_url(
            "https://polygon.codeforces.com/p/demo/a-plus-b",
            package_type="linux",
        )

        self.assertEqual(content, b"zip")
        creds_mock.assert_called_once_with(None, None)
        download_mock.assert_called_once_with(
            problem_url="https://polygon.codeforces.com/p/demo/a-plus-b",
            login="env-login",
            password="env-password",
            pin=None,
            revision=None,
            package_type="linux",
        )


if __name__ == "__main__":
    unittest.main()
