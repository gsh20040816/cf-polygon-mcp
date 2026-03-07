import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.downloads import (
    DOWNLOAD_INFO_FIXED_FIELDS,
    download_contest_statements_pdf_info,
    download_problem_package_by_url,
    download_problem_package_info_by_url,
)
from src.mcp.utils.problem_packages import download_problem_package_info
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

    @patch("src.mcp.utils.downloads.download_problem_package_by_url", return_value=b"zip-bytes")
    def test_download_problem_package_info_by_url_returns_metadata(self, download_mock):
        result = download_problem_package_info_by_url(
            "https://polygon.codeforces.com/p/demo/a-plus-b",
            pin="1234",
            revision=7,
            package_type="linux",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "download_problem_package_info_by_url")
        self.assertEqual(result["message"], "package.zip 下载元数据已生成")
        for field_name in DOWNLOAD_INFO_FIXED_FIELDS:
            self.assertIn(field_name, result)
            self.assertIn(field_name, result["result"])
        self.assertEqual(result["source_kind"], "url")
        self.assertEqual(
            result["source_ref"],
            "https://polygon.codeforces.com/p/demo/a-plus-b",
        )
        self.assertEqual(
            result["source_url"],
            "https://polygon.codeforces.com/p/demo/a-plus-b",
        )
        self.assertEqual(result["filename"], "package.zip")
        self.assertEqual(result["content_kind"], "zip")
        self.assertEqual(result["size_bytes"], 9)
        self.assertEqual(result["revision"], 7)
        self.assertEqual(result["package_type"], "linux")
        self.assertEqual(result["result"]["filename"], "package.zip")
        self.assertNotIn("pin", result)
        self.assertNotIn("pin", result["result"])
        self.assertEqual(
            result["sha256"],
            "4b9a4ac59f3c3aa32273260df6cf4bf358d1c46f8415126aa35b6380d0abb8f7",
        )
        download_mock.assert_called_once()

    @patch("src.mcp.utils.problem_packages.download_problem_package", return_value=b"zip-bytes")
    def test_download_problem_package_info_returns_metadata(self, download_mock):
        result = download_problem_package_info(
            problem_id=321,
            package_id=9,
            pin="4321",
            package_type="standard",
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["action"], "download_problem_package_info")
        for field_name in DOWNLOAD_INFO_FIXED_FIELDS:
            self.assertIn(field_name, result)
            self.assertIn(field_name, result["result"])
        self.assertEqual(result["source_kind"], "problem_package")
        self.assertEqual(result["source_ref"], "problem:321/package:9")
        self.assertEqual(result["problem_id"], 321)
        self.assertEqual(result["package_id"], 9)
        self.assertEqual(result["package_type"], "standard")
        self.assertNotIn("pin", result)
        self.assertNotIn("pin", result["result"])
        download_mock.assert_called_once_with(
            problem_id=321,
            package_id=9,
            pin="4321",
            package_type="standard",
        )

    @patch("src.mcp.utils.downloads.download_contest_statements_pdf", return_value=b"%PDF-1.7")
    def test_download_contest_statements_pdf_info_returns_metadata(self, download_mock):
        result = download_contest_statements_pdf_info(
            "https://polygon.codeforces.com/c/demo-contest",
            language="english",
        )

        self.assertEqual(result["status"], "success")
        for field_name in DOWNLOAD_INFO_FIXED_FIELDS:
            self.assertIn(field_name, result)
        self.assertEqual(result["filename"], "statements.pdf")
        self.assertEqual(result["content_kind"], "pdf")
        self.assertEqual(result["language"], "english")
        self.assertEqual(result["size_bytes"], 8)
        self.assertEqual(
            result["sha256"],
            "86edbaa24831badfa0a8b04bb410141e2ee4182b6d0014493fe262a7a331c20b",
        )
        download_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
