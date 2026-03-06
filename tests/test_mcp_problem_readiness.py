from datetime import datetime
import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_readiness import check_problem_readiness
from src.polygon.models import (
    Package,
    PackageState,
    PackageType,
    ProblemInfo,
    Solution,
    SolutionTag,
    SourceType,
    Statement,
    Test,
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


class MpcProblemReadinessTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_ready_problem(self, session_mock):
        session = Mock()
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
        self.assertEqual(result["blocking_issues"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["details"]["tests"]["sample_count"], 1)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_blocking_issues(self, session_mock):
        session = Mock()
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

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_non_blocking_warnings(self, session_mock):
        session = Mock()
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


if __name__ == "__main__":
    unittest.main()
