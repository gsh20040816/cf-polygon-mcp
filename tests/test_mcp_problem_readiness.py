from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_readiness import check_problem_readiness
from src.polygon.models import (
    AccessType,
    FeedbackPolicy,
    File,
    Package,
    PackageState,
    PackageType,
    PointsPolicy,
    ProblemInfo,
    Solution,
    SolutionTag,
    SourceType,
    Statement,
    Test,
    TestGroup,
)


class _StatementMap:
    def __init__(self, items):
        self._items = items

    def as_dict(self):
        return self._items


def _ready_package() -> Package:
    return Package(
        id=1,
        revision=1,
        creationTimeSeconds=datetime(2024, 1, 1, 0, 0, 1),
        state=PackageState.READY,
        comment="ok",
        type=PackageType.STANDARD,
    )


def _solution(name: str, tag: SolutionTag) -> Solution:
    return Solution(
        name=name,
        modificationTimeSeconds=datetime(2024, 1, 1, 0, 0, 1),
        length=100,
        sourceType=SourceType.SOLUTION,
        tag=tag,
    )


def _problem_meta(
    revision: int = 1,
    latest_package: int | None = 1,
    modified: bool = True,
):
    problem = Mock()
    problem.id = 1
    problem.name = "A + B"
    problem.accessType = AccessType.OWNER
    problem.revision = revision
    problem.latestPackage = latest_package
    problem.modified = modified
    return problem


def _source_file(name: str):
    return File(
        name=name,
        modificationTimeSeconds=datetime(2024, 1, 1, 0, 0, 1),
        length=100,
        sourceType=SourceType.MAIN,
    )


def _problem_files(*source_names: str):
    files = Mock()
    files.resourceFiles = []
    files.sourceFiles = [_source_file(name) for name in source_names]
    files.auxFiles = []
    return files


class MpcProblemReadinessTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_ready_problem(self, session_mock):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta(modified=False)]
        session.get_info.return_value = ProblemInfo(
            inputFile="input.txt",
            outputFile="output.txt",
            interactive=False,
            timeLimit=2000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap(
            {
                "english": Statement(
                    encoding="utf-8",
                    name="A + B",
                    legend="desc",
                    input="in",
                    output="out",
                )
            }
        )
        session.get_validator.return_value = "validator.cpp"
        session.get_checker.return_value = "checker.cpp"
        session.get_interactor.return_value = ""
        session.get_extra_validators.return_value = ["validator-extra.cpp"]
        session.get_files.return_value = _problem_files(
            "validator.cpp",
            "checker.cpp",
            "validator-extra.cpp",
        )
        session.get_tests.return_value = [
            Test(
                index=1,
                manual=True,
                input="1 2",
                useInStatements=True,
                inputForStatement="1 2",
                outputForStatement="3",
                verifyInputOutputForStatements=True,
            ),
        ]
        session.get_solutions.return_value = [
            _solution("main.cpp", SolutionTag.MA),
            _solution("wa.cpp", SolutionTag.WA),
        ]
        session.get_validator_tests.return_value = [Mock()]
        session.get_checker_tests.return_value = [Mock()]
        session.get_packages.return_value = [_ready_package()]
        session.get_general_tutorial.return_value = "tutorial"
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertEqual(result["blocking_issues"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["summary"]["status"], "ready")
        self.assertEqual(result["summary"]["recommendation"], "ready_for_release")
        self.assertEqual(result["summary"]["blocking_issue_count"], 0)
        self.assertEqual(result["summary"]["warning_count"], 0)
        self.assertEqual(result["details"]["tests"]["sample_count"], 1)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_blocking_issues(self, session_mock):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta()]
        session.get_info.return_value = ProblemInfo(
            inputFile="input.txt",
            outputFile="output.txt",
            interactive=True,
            timeLimit=2000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap({})
        session.get_validator.return_value = ""
        session.get_checker.return_value = ""
        session.get_interactor.return_value = ""
        session.get_extra_validators.return_value = []
        session.get_files.return_value = _problem_files()
        session.get_tests.return_value = []
        session.get_solutions.return_value = []
        session.get_packages.return_value = []
        session.get_general_tutorial.return_value = ""
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("缺少题面", result["blocking_issues"])
        self.assertIn("未设置 validator", result["blocking_issues"])
        self.assertIn("交互题未设置 interactor", result["blocking_issues"])
        self.assertIn("测试集 tests 中没有测试", result["blocking_issues"])
        self.assertIn("缺少正确解", result["blocking_issues"])
        self.assertIn("通用题解为空", result["warnings"])
        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertEqual(result["summary"]["recommendation"], "fix_blocking_issues")
        self.assertGreater(result["summary"]["blocking_issue_count"], 0)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_non_blocking_warnings(self, session_mock):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta(modified=False, latest_package=None)]
        session.get_info.return_value = ProblemInfo(
            inputFile="stdin",
            outputFile="stdout",
            interactive=False,
            timeLimit=1000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap(
            {
                "russian": Statement(
                    encoding="utf-8",
                    name="sum",
                    legend="desc",
                    input="in",
                    output="out",
                )
            }
        )
        session.get_validator.return_value = "validator.cpp"
        session.get_checker.return_value = ""
        session.get_interactor.return_value = "interactor.cpp"
        session.get_extra_validators.return_value = []
        session.get_files.return_value = _problem_files("validator.cpp")
        session.get_tests.return_value = [
            Test(index=1, manual=True, input="1 2", useInStatements=False),
        ]
        session.get_solutions.return_value = [_solution("ok.cpp", SolutionTag.OK)]
        session.get_validator_tests.return_value = []
        session.get_packages.return_value = []
        session.get_general_tutorial.return_value = ""
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertIn("缺少 english 题面", result["warnings"])
        self.assertIn("未显式设置 checker，将依赖 Polygon 默认比较器", result["warnings"])
        self.assertIn("当前题目不是交互题，但设置了 interactor", result["warnings"])
        self.assertIn("测试集 tests 中没有用于题面的样例", result["warnings"])
        self.assertIn("缺少主解（MA）", result["warnings"])
        self.assertIn("缺少错误解或边界解，校验覆盖可能不足", result["warnings"])
        self.assertIn("未配置 validator 测试", result["warnings"])
        self.assertIn("还没有 READY 状态的题目包", result["warnings"])
        self.assertEqual(result["summary"]["status"], "warnings")
        self.assertEqual(result["summary"]["recommendation"], "review_warnings")
        self.assertEqual(result["summary"]["blocking_issue_count"], 0)
        self.assertGreater(result["summary"]["warning_count"], 0)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_ignores_interactor_errors_for_non_interactive_problem(
        self,
        session_mock,
    ):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta(modified=False)]
        session.get_info.return_value = ProblemInfo(
            inputFile="stdin",
            outputFile="stdout",
            interactive=False,
            timeLimit=1000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap(
            {
                "english": Statement(
                    encoding="utf-8",
                    name="sum",
                    legend="desc",
                    input="in",
                    output="out",
                )
            }
        )
        session.get_validator.return_value = "validator.cpp"
        session.get_checker.return_value = "checker.cpp"
        session.get_interactor.side_effect = RuntimeError("not interactive")
        session.get_extra_validators.return_value = []
        session.get_files.return_value = _problem_files("validator.cpp", "checker.cpp")
        session.get_tests.return_value = [
            Test(index=1, manual=True, input="1 2", useInStatements=True),
        ]
        session.get_solutions.return_value = [
            _solution("main.cpp", SolutionTag.MA),
            _solution("wa.cpp", SolutionTag.WA),
        ]
        session.get_validator_tests.return_value = [Mock()]
        session.get_checker_tests.return_value = [Mock()]
        session.get_packages.return_value = [_ready_package()]
        session.get_general_tutorial.return_value = "tutorial"
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertNotIn("interactor 检查失败: not interactive", result["blocking_issues"])
        self.assertEqual(result["details"]["interactor"]["status"], "ignored")

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_local_workflow_gaps(self, session_mock):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta()]
        session.get_info.return_value = ProblemInfo(
            inputFile="stdin",
            outputFile="stdout",
            interactive=True,
            timeLimit=2000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap(
            {
                "english": Statement(
                    encoding="utf-8",
                    name="Interactive",
                    legend="desc",
                    input="in",
                    output="out",
                    scoring=None,
                )
            }
        )
        session.get_validator.return_value = "validator.cpp"
        session.get_checker.return_value = "checker.cpp"
        session.get_interactor.return_value = "interactor.cpp"
        session.get_extra_validators.return_value = ["validator-extra.cpp"]
        session.get_files.return_value = _problem_files("validator.cpp", "checker.cpp")
        session.get_tests.return_value = [
            Test(
                index=1,
                manual=False,
                useInStatements=True,
                inputForStatement="1",
                verifyInputOutputForStatements=False,
                points=30,
            )
        ]
        session.view_script.return_value = b""
        session.get_solutions.return_value = [
            _solution("main.cpp", SolutionTag.MA),
            _solution("wa.cpp", SolutionTag.WA),
        ]
        session.get_validator_tests.return_value = [Mock()]
        session.get_checker_tests.return_value = [Mock()]
        session.get_packages.return_value = [_ready_package()]
        session.get_general_tutorial.return_value = "tutorial"
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("english 题面缺少交互协议（interaction）", result["blocking_issues"])
        self.assertIn(
            "以下已配置源码文件不存在于题目源文件列表中: interactor: interactor.cpp, extra validator: validator-extra.cpp",
            result["blocking_issues"],
        )
        self.assertIn("以下样例缺少题面输出展示内容: 1", result["warnings"])
        self.assertIn("以下样例未启用题面输入输出校验: 1", result["warnings"])
        self.assertIn("测试集 tests 存在生成测试，但生成脚本为空", result["warnings"])
        self.assertIn(
            "题目存在带分测试，但以下题面缺少 scoring 字段: english",
            result["warnings"],
        )

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_test_group_gaps(self, session_mock):
        session = Mock()
        session.client.get_problems.return_value = [_problem_meta(modified=False)]
        session.get_info.return_value = ProblemInfo(
            inputFile="stdin",
            outputFile="stdout",
            interactive=False,
            timeLimit=2000,
            memoryLimit=256,
        )
        session.get_statements.return_value = _StatementMap(
            {
                "english": Statement(
                    encoding="utf-8",
                    name="Grouped",
                    legend="desc",
                    input="in",
                    output="out",
                )
            }
        )
        session.get_validator.return_value = "validator.cpp"
        session.get_checker.return_value = "checker.cpp"
        session.get_interactor.return_value = ""
        session.get_extra_validators.return_value = []
        session.get_files.return_value = _problem_files("validator.cpp", "checker.cpp")
        session.get_tests.return_value = [
            Test(
                index=1,
                manual=True,
                input="1 2",
                useInStatements=True,
                inputForStatement="1 2",
                outputForStatement="3",
                verifyInputOutputForStatements=True,
                group="samples",
            ),
            Test(
                index=2,
                manual=True,
                input="2 3",
                useInStatements=False,
                group="missing-group",
            ),
        ]
        session.view_test_groups.return_value = [
            TestGroup(
                name="samples",
                pointsPolicy=PointsPolicy.EACH_TEST,
                feedbackPolicy=FeedbackPolicy.POINTS,
                dependencies=[],
            ),
            TestGroup(
                name="unused",
                pointsPolicy=PointsPolicy.COMPLETE_GROUP,
                feedbackPolicy=FeedbackPolicy.ICPC,
                dependencies=["ghost"],
            ),
        ]
        session.get_solutions.return_value = [
            _solution("main.cpp", SolutionTag.MA),
            _solution("wa.cpp", SolutionTag.WA),
        ]
        session.get_validator_tests.return_value = [Mock()]
        session.get_checker_tests.return_value = [Mock()]
        session.get_packages.return_value = [_ready_package()]
        session.get_general_tutorial.return_value = "tutorial"
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("以下测试引用了未定义的测试组: missing-group", result["blocking_issues"])
        self.assertIn("以下测试组依赖了未定义的测试组: unused -> ghost", result["blocking_issues"])
        self.assertIn("以下测试组未分配任何测试: unused", result["warnings"])
        self.assertEqual(result["details"]["test_groups"]["defined_count"], 2)


if __name__ == "__main__":
    unittest.main()
