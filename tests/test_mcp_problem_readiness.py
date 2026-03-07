import unittest
from unittest.mock import Mock, patch

from src.mcp.utils.problem_readiness import check_problem_readiness
from src.polygon.models import PackageState, SolutionTag
from tests.fake_problem_session import (
    FakeProblemSession,
    make_file,
    make_package,
    make_problem,
    make_problem_files,
    make_problem_info,
    make_solution,
    make_statement,
    make_test,
    make_test_group,
)


class MpcProblemReadinessTest(unittest.TestCase):
    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_ready_problem(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(
                input_file="input.txt",
                output_file="output.txt",
                interactive=False,
                time_limit=2000,
                memory_limit=256,
            ),
            statements={"english": make_statement()},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="",
            extra_validators=["validator-extra.cpp"],
            files=make_problem_files("validator.cpp", "checker.cpp", "validator-extra.cpp"),
            tests=[
                make_test(
                    index=1,
                    manual=True,
                    input_text="1 2",
                    use_in_statements=True,
                    input_for_statement="1 2",
                    output_for_statement="3",
                    verify_statement_io=True,
                )
            ],
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
                make_solution("re.cpp", SolutionTag.RE),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertEqual(result["stage"], "completed")
        self.assertEqual(result["decision"], "ready_for_release")
        self.assertEqual(result["can_retry"], False)
        self.assertEqual(result["recovery_actions"], [])
        self.assertEqual(result["blocking_issues"], [])
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["summary"]["status"], "ready")
        self.assertEqual(result["summary"]["recommendation"], "ready_for_release")
        self.assertEqual(result["summary"]["blocking_issue_count"], 0)
        self.assertEqual(result["summary"]["warning_count"], 0)
        self.assertEqual(result["summary"]["next_steps"], ["可以进入构建与发布流程"])
        self.assertEqual(result["details"]["tests"]["sample_count"], 1)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_blocking_issues(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=True)],
            info=make_problem_info(
                input_file="input.txt",
                output_file="output.txt",
                interactive=True,
                time_limit=2000,
                memory_limit=256,
            ),
            statements={},
            validator="",
            checker="",
            interactor="",
            extra_validators=[],
            files=make_problem_files(),
            tests=[],
            solutions=[],
            packages=[],
            general_tutorial="",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertEqual(result["decision"], "fix_blocking_issues")
        self.assertEqual(result["can_retry"], True)
        self.assertEqual(result["recovery_actions"][0]["action"], "fix_blocking_issues")
        self.assertIn("缺少题面", result["blocking_issues"])
        self.assertIn("未设置 validator", result["blocking_issues"])
        self.assertIn("交互题未设置 interactor", result["blocking_issues"])
        self.assertIn("测试集 tests 中没有测试", result["blocking_issues"])
        self.assertIn("缺少正确解", result["blocking_issues"])
        self.assertIn("通用题解为空", result["warnings"])
        self.assertEqual(result["summary"]["status"], "blocked")
        self.assertEqual(result["summary"]["recommendation"], "fix_blocking_issues")
        self.assertGreater(result["summary"]["blocking_issue_count"], 0)
        self.assertIn("补齐题面与必需配置后重新检查 readiness", result["summary"]["next_steps"])

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_non_blocking_warnings(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=False, latest_package=None)],
            info=make_problem_info(
                input_file="stdin",
                output_file="stdout",
                interactive=False,
                time_limit=1000,
                memory_limit=256,
            ),
            statements={
                "russian": make_statement(name="sum"),
            },
            validator="validator.cpp",
            checker="",
            interactor="interactor.cpp",
            extra_validators=[],
            files=make_problem_files("validator.cpp"),
            tests=[make_test(index=1, manual=True, input_text="1 2", use_in_statements=False)],
            solutions=[make_solution("ok.cpp", SolutionTag.OK)],
            validator_tests=[],
            packages=[],
            general_tutorial="",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertEqual(result["decision"], "review_warnings")
        self.assertEqual(result["can_retry"], True)
        self.assertEqual(result["recovery_actions"][0]["action"], "review_warnings")
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
        self.assertIn("评估并处理 warnings，确认是否允许继续发布", result["summary"]["next_steps"])

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_ignores_interactor_errors_for_non_interactive_problem(
        self,
        session_mock,
    ):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(interactive=False),
            statements={"english": make_statement(name="sum")},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor=RuntimeError("not interactive"),
            extra_validators=[],
            files=make_problem_files("validator.cpp", "checker.cpp"),
            tests=[make_test(index=1, manual=True, input_text="1 2", use_in_statements=True)],
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertTrue(result["ready"])
        self.assertNotIn("interactor 检查失败: not interactive", result["blocking_issues"])
        self.assertEqual(result["details"]["interactor"]["status"], "ignored")

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_local_workflow_gaps(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=True)],
            info=make_problem_info(interactive=True, time_limit=2000),
            statements={"english": make_statement(name="Interactive", scoring=None)},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="interactor.cpp",
            extra_validators=["validator-extra.cpp"],
            files=make_problem_files("validator.cpp", "checker.cpp"),
            tests=[
                make_test(
                    index=1,
                    manual=False,
                    use_in_statements=True,
                    input_for_statement="1",
                    output_for_statement=None,
                    verify_statement_io=False,
                    points=30,
                )
            ],
            scripts={"tests": b""},
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
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
    def test_check_problem_readiness_reports_statement_resource_and_generator_mismatches(
        self,
        session_mock,
    ):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(time_limit=2000),
            statements={
                "english": make_statement(
                    name="Generator",
                    legend=r"See \includegraphics{diagram.png}.",
                )
            },
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="",
            extra_validators=[],
            statement_resources=[],
            files=make_problem_files(
                "validator.cpp",
                "checker.cpp",
                "gen.cpp",
                resource_names=["existing.png"],
            ),
            tests=[
                make_test(
                    index=1,
                    manual=True,
                    input_text="1 2",
                    use_in_statements=True,
                    input_for_statement="1 2",
                    output_for_statement="3",
                    verify_statement_io=True,
                ),
                make_test(index=2, manual=False, script_line="gen 10"),
                make_test(index=3, manual=False, script_line="missing_gen 20"),
            ],
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
                make_solution("re.cpp", SolutionTag.RE),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
            scripts={"tests": b"gen 10\n"},
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("题面引用了不存在的资源文件: diagram.png", result["blocking_issues"])
        self.assertIn("以下生成测试的 scriptLine 未出现在当前生成脚本中: 3", result["warnings"])
        self.assertIn(
            "生成测试脚本引用了不存在的相关文件或生成器: missing_gen",
            result["warnings"],
        )
        self.assertEqual(result["details"]["statement_resources"]["missing_references"], ["diagram.png"])
        self.assertEqual(result["details"]["script"]["generated_tests_missing_from_script"], [3])
        self.assertEqual(result["details"]["script"]["missing_related_file_references"], ["missing_gen"])

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_test_group_gaps(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(time_limit=2000),
            statements={"english": make_statement(name="Grouped")},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="",
            extra_validators=[],
            files=make_problem_files("validator.cpp", "checker.cpp"),
            tests=[
                make_test(
                    index=1,
                    manual=True,
                    input_text="1 2",
                    use_in_statements=True,
                    input_for_statement="1 2",
                    output_for_statement="3",
                    verify_statement_io=True,
                    group="samples",
                ),
                make_test(
                    index=2,
                    manual=True,
                    input_text="2 3",
                    use_in_statements=False,
                    group="missing-group",
                ),
            ],
            test_groups={
                "tests": [
                    make_test_group("samples", dependencies=[]),
                    make_test_group("unused", dependencies=["ghost"]),
                ]
            },
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("以下测试引用了未定义的测试组: missing-group", result["blocking_issues"])
        self.assertIn("以下测试组依赖了未定义的测试组: unused -> ghost", result["blocking_issues"])
        self.assertIn("以下测试组未分配任何测试: unused", result["warnings"])
        self.assertEqual(result["details"]["test_groups"]["defined_count"], 2)

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_group_cycles_and_solution_coverage(
        self,
        session_mock,
    ):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(time_limit=2000),
            statements={"english": make_statement(name="Cycle")},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="",
            extra_validators=[],
            statement_resources=[make_file("diagram.png", source_type=None)],
            files=make_problem_files(
                "validator.cpp",
                "checker.cpp",
                resource_names=["diagram.png"],
            ),
            tests=[
                make_test(
                    index=1,
                    manual=True,
                    input_text="1 2",
                    use_in_statements=True,
                    input_for_statement="1 2",
                    output_for_statement="3",
                    verify_statement_io=True,
                    group="pretests",
                ),
                make_test(index=2, manual=True, input_text="2 3", group="tests"),
            ],
            test_groups={
                "tests": [
                    make_test_group("pretests", dependencies=["tests"]),
                    make_test_group("tests", dependencies=["pretests"]),
                ]
            },
            solutions=[
                make_solution("main.cpp", SolutionTag.MA),
                make_solution("main2.cpp", SolutionTag.MA),
                make_solution("wa.cpp", SolutionTag.WA),
            ],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("以下测试组依赖成环: pretests -> tests -> pretests", result["blocking_issues"])
        self.assertIn("主解（MA）数量异常: 2", result["warnings"])
        self.assertIn("错误解或边界解类型较少，建议至少覆盖两类非通过判定", result["warnings"])
        self.assertEqual(
            result["details"]["test_groups"]["cyclic_dependencies"],
            ["pretests -> tests -> pretests"],
        )
        self.assertEqual(result["details"]["solutions"]["main_solution_count"], 2)
        self.assertEqual(result["details"]["solutions"]["non_accepted_tag_counts"], {"WA": 1})

    @patch("src.mcp.utils.problem_readiness.get_problem_session")
    def test_check_problem_readiness_reports_error_sections_in_summary(self, session_mock):
        session = FakeProblemSession(
            problems=[make_problem(modified=False)],
            info=make_problem_info(),
            statements={"english": make_statement()},
            validator="validator.cpp",
            checker="checker.cpp",
            interactor="",
            extra_validators=[],
            files=RuntimeError("files broken"),
            tests=[make_test(index=1, manual=True, input_text="1 2", use_in_statements=False)],
            solutions=[make_solution("main.cpp", SolutionTag.MA)],
            validator_tests=[Mock()],
            checker_tests=[Mock()],
            packages=[make_package(1, PackageState.READY)],
            general_tutorial="tutorial",
        )
        session_mock.return_value = session

        result = check_problem_readiness(problem_id=1)

        self.assertFalse(result["ready"])
        self.assertIn("题目文件 检查失败: files broken", result["blocking_issues"])
        self.assertEqual(result["details"]["题目文件"]["status"], "error")
        self.assertIn("题目文件", result["summary"]["sections_with_errors"])


if __name__ == "__main__":
    unittest.main()
