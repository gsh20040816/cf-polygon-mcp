from __future__ import annotations

from typing import Any, Optional

from src.mcp.utils.common import get_problem_session
from src.polygon.models import PackageState, SolutionTag


def _append_check_error(
    section: str,
    exc: Exception,
    blocking_issues: list[str],
    details: dict[str, Any],
) -> None:
    message = f"{section} 检查失败: {exc}"
    blocking_issues.append(message)
    details[section] = {"status": "error", "error": str(exc)}


def check_problem_readiness(
    problem_id: int,
    pin: Optional[str] = None,
    testset: str = "tests",
) -> dict[str, Any]:
    """
    检查题目是否具备基本的出题与发布条件。

    Returns:
        dict: 包含 blocking_issues、warnings 和各项检查明细。
    """
    session = get_problem_session(problem_id, pin)
    blocking_issues: list[str] = []
    warnings: list[str] = []
    details: dict[str, Any] = {"problem_id": problem_id, "testset": testset}

    try:
        info = session.get_info()
        details["info"] = {
            "input_file": info.inputFile,
            "output_file": info.outputFile,
            "interactive": info.interactive,
            "time_limit": info.timeLimit,
            "memory_limit": info.memoryLimit,
        }
        if not info.inputFile:
            blocking_issues.append("未设置输入文件名")
        if not info.outputFile:
            blocking_issues.append("未设置输出文件名")
        if info.timeLimit <= 0:
            blocking_issues.append("时间限制必须大于 0")
        if info.memoryLimit <= 0:
            blocking_issues.append("内存限制必须大于 0")
    except Exception as exc:
        _append_check_error("题目信息", exc, blocking_issues, details)
        info = None

    try:
        statements = session.get_statements().as_dict()
        details["statements"] = {
            "languages": sorted(statements.keys()),
            "count": len(statements),
        }
        if not statements:
            blocking_issues.append("缺少题面")
        else:
            if "english" not in statements:
                warnings.append("缺少 english 题面")
            for lang, statement in statements.items():
                missing_fields = [
                    field_name
                    for field_name in ("name", "legend", "input", "output")
                    if not getattr(statement, field_name)
                ]
                if missing_fields:
                    blocking_issues.append(
                        f"{lang} 题面缺少字段: {', '.join(missing_fields)}"
                    )
    except Exception as exc:
        _append_check_error("题面", exc, blocking_issues, details)

    try:
        validator = session.get_validator()
        details["validator"] = validator
        if not validator:
            blocking_issues.append("未设置 validator")
    except Exception as exc:
        _append_check_error("validator", exc, blocking_issues, details)
        validator = None

    try:
        checker = session.get_checker()
        details["checker"] = checker
        if not checker:
            warnings.append("未显式设置 checker，将依赖 Polygon 默认比较器")
    except Exception as exc:
        _append_check_error("checker", exc, blocking_issues, details)
        checker = None

    try:
        interactor = session.get_interactor()
        details["interactor"] = interactor
        if info is not None and info.interactive and not interactor:
            blocking_issues.append("交互题未设置 interactor")
        if info is not None and not info.interactive and interactor:
            warnings.append("当前题目不是交互题，但设置了 interactor")
    except Exception as exc:
        _append_check_error("interactor", exc, blocking_issues, details)

    try:
        tests = session.get_tests(testset=testset)
        statement_samples = sum(1 for test in tests if test.useInStatements)
        details["tests"] = {
            "count": len(tests),
            "manual_count": sum(1 for test in tests if test.manual),
            "sample_count": statement_samples,
        }
        if not tests:
            blocking_issues.append(f"测试集 {testset} 中没有测试")
        elif statement_samples == 0:
            warnings.append(f"测试集 {testset} 中没有用于题面的样例")
    except Exception as exc:
        _append_check_error("测试", exc, blocking_issues, details)

    try:
        solutions = session.get_solutions()
        accepted_solution_count = sum(
            1 for solution in solutions if solution.tag in (SolutionTag.MA, SolutionTag.OK)
        )
        has_main_solution = any(solution.tag == SolutionTag.MA for solution in solutions)
        has_non_accepted_solution = any(
            solution.tag not in (SolutionTag.MA, SolutionTag.OK) for solution in solutions
        )
        details["solutions"] = {
            "count": len(solutions),
            "accepted_count": accepted_solution_count,
            "has_main_solution": has_main_solution,
            "has_non_accepted_solution": has_non_accepted_solution,
        }
        if accepted_solution_count == 0:
            blocking_issues.append("缺少正确解")
        if not has_main_solution:
            warnings.append("缺少主解（MA）")
        if not has_non_accepted_solution:
            warnings.append("缺少错误解或边界解，校验覆盖可能不足")
    except Exception as exc:
        _append_check_error("解法", exc, blocking_issues, details)

    if validator:
        try:
            validator_tests = session.get_validator_tests()
            details["validator_tests"] = {"count": len(validator_tests)}
            if not validator_tests:
                warnings.append("未配置 validator 测试")
        except Exception as exc:
            _append_check_error("validator 测试", exc, blocking_issues, details)

    if checker:
        try:
            checker_tests = session.get_checker_tests()
            details["checker_tests"] = {"count": len(checker_tests)}
            if not checker_tests:
                warnings.append("未配置 checker 测试")
        except Exception as exc:
            _append_check_error("checker 测试", exc, blocking_issues, details)

    try:
        packages = session.get_packages()
        ready_packages = [package for package in packages if package.state == PackageState.READY]
        details["packages"] = {
            "count": len(packages),
            "ready_count": len(ready_packages),
        }
        if not ready_packages:
            warnings.append("还没有 READY 状态的题目包")
    except Exception as exc:
        _append_check_error("题目包", exc, blocking_issues, details)

    try:
        tutorial = session.get_general_tutorial()
        details["general_tutorial"] = {"present": bool(tutorial.strip())}
        if not tutorial.strip():
            warnings.append("通用题解为空")
    except Exception as exc:
        _append_check_error("通用题解", exc, blocking_issues, details)

    return {
        "status": "success",
        "ready": not blocking_issues,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "details": details,
    }
