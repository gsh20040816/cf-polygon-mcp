from __future__ import annotations

import re
import shlex
from collections import Counter
from typing import Any, Optional

from src.mcp.utils.common import build_recovery_action, get_problem_session
from src.polygon.models import PackageState, SolutionTag

_STATEMENT_RESOURCE_PATTERNS = (
    re.compile(r"\\includegraphics(?:\[[^\]]*])?\{([^}]+)\}"),
    re.compile(r"\\lstinputlisting(?:\[[^\]]*])?\{([^}]+)\}"),
    re.compile(r"\\inputminted(?:\[[^\]]*])?\{[^}]+\}\{([^}]+)\}"),
    re.compile(r"<img[^>]+src=[\"']([^\"']+)[\"']", re.IGNORECASE),
    re.compile(r"!\[[^\]]*\]\(([^)]+)\)"),
)
_SCRIPT_FILENAME_PATTERN = re.compile(r"([A-Za-z_][A-Za-z0-9_./-]*\.[A-Za-z0-9_+-]+)")
_GENERIC_SCRIPT_COMMANDS = {
    "bash",
    "cat",
    "cc",
    "clang",
    "clang++",
    "cmd",
    "cmake",
    "cp",
    "cut",
    "deno",
    "echo",
    "g++",
    "gcc",
    "go",
    "grep",
    "head",
    "java",
    "javac",
    "make",
    "mkdir",
    "mv",
    "node",
    "perl",
    "php",
    "powershell",
    "printf",
    "pwsh",
    "pypy",
    "pypy3",
    "python",
    "python3",
    "rm",
    "ruby",
    "sed",
    "sh",
    "sort",
    "tail",
    "tar",
    "tee",
    "touch",
    "tr",
    "unzip",
    "xargs",
    "zip",
    "zsh",
}


def _append_check_error(
    section: str,
    exc: Exception,
    blocking_issues: list[str],
    details: dict[str, Any],
) -> None:
    message = f"{section} 检查失败: {exc}"
    blocking_issues.append(message)
    details[section] = {"status": "error", "error": str(exc)}


def _has_text(value: Optional[str]) -> bool:
    return bool(value and value.strip())


def _normalize_text(value: Optional[str]) -> Optional[str]:
    if not _has_text(value):
        return None
    return value.strip()


def _normalize_file_reference(value: str) -> str:
    normalized = value.strip().strip("\"'")
    normalized = normalized.split("?", maxsplit=1)[0]
    normalized = normalized.split("#", maxsplit=1)[0]
    normalized = normalized.replace("\\", "/")
    return normalized.rsplit("/", maxsplit=1)[-1]


def _build_file_reference_keys(value: str) -> set[str]:
    normalized = _normalize_file_reference(value).lower()
    if not normalized:
        return set()
    keys = {normalized}
    if "." in normalized:
        keys.add(normalized.rsplit(".", maxsplit=1)[0])
    return keys


def _find_missing_file_references(
    references: list[str],
    available_names: set[str] | list[str],
) -> list[str]:
    available_keys = set()
    for name in available_names:
        available_keys.update(_build_file_reference_keys(name))

    missing: list[str] = []
    for reference in references:
        if not (_build_file_reference_keys(reference) & available_keys):
            missing.append(reference)
    return missing


def _extract_statement_resource_references(statements: dict[str, Any]) -> list[str]:
    references: set[str] = set()
    for statement in statements.values():
        for field_name in (
            "legend",
            "input",
            "output",
            "scoring",
            "interaction",
            "notes",
            "tutorial",
        ):
            value = getattr(statement, field_name, None)
            if not _has_text(value):
                continue
            for pattern in _STATEMENT_RESOURCE_PATTERNS:
                for match in pattern.findall(value):
                    normalized = _normalize_text(match)
                    if normalized is not None:
                        references.add(normalized)
    return sorted(references)


def _normalize_script_lines(script_text: str) -> set[str]:
    return {
        line.strip()
        for line in script_text.splitlines()
        if _has_text(line)
    }


def _extract_script_related_references(script_line: Optional[str]) -> list[str]:
    if not _has_text(script_line):
        return []

    line = script_line.strip()
    references = {
        _normalize_file_reference(match)
        for match in _SCRIPT_FILENAME_PATTERN.findall(line)
    }
    try:
        tokens = shlex.split(line, posix=True)
    except ValueError:
        tokens = line.split()

    command: Optional[str] = None
    for token in tokens:
        stripped = token.strip()
        if not stripped or stripped in {"|", "||", "&&", ";"}:
            break
        if stripped.startswith((">", "<")):
            break
        if "=" in stripped and "/" not in stripped and stripped.index("=") > 0:
            continue
        candidate = stripped.lstrip("@")
        if candidate.startswith("-"):
            continue
        command = candidate
        break

    if command is not None:
        basename = _normalize_file_reference(command)
        if basename and basename.lower() not in _GENERIC_SCRIPT_COMMANDS and not basename.startswith("$"):
            references.add(basename)

    return sorted(references)


def _canonicalize_cycle(cycle: list[str]) -> str:
    if len(cycle) <= 1:
        return " -> ".join(cycle)
    base = cycle[:-1]
    pivot = min(range(len(base)), key=base.__getitem__)
    rotated = base[pivot:] + base[:pivot]
    rotated.append(rotated[0])
    return " -> ".join(rotated)


def _find_test_group_cycles(group_dependencies: dict[str, list[str]]) -> list[str]:
    state: dict[str, int] = {}
    stack: list[str] = []
    cycles: set[str] = set()

    def dfs(group_name: str) -> None:
        current_state = state.get(group_name, 0)
        if current_state == 1:
            start = stack.index(group_name)
            cycles.add(_canonicalize_cycle(stack[start:] + [group_name]))
            return
        if current_state == 2:
            return

        state[group_name] = 1
        stack.append(group_name)
        for dependency in group_dependencies.get(group_name, []):
            if dependency in group_dependencies:
                dfs(dependency)
        stack.pop()
        state[group_name] = 2

    for group_name in sorted(group_dependencies):
        if state.get(group_name, 0) == 0:
            dfs(group_name)

    return sorted(cycles)


def _serialize_problem(problem: Any) -> dict[str, Any]:
    return {
        "id": problem.id,
        "name": problem.name,
        "access_type": problem.accessType.value,
        "revision": problem.revision,
        "latest_package": problem.latestPackage,
        "modified": problem.modified,
    }


def _build_summary(
    blocking_issues: list[str],
    warnings: list[str],
    details: dict[str, Any],
) -> dict[str, Any]:
    error_sections = sorted(
        key
        for key, value in details.items()
        if isinstance(value, dict) and value.get("status") == "error"
    )
    if blocking_issues:
        status = "blocked"
        recommendation = "fix_blocking_issues"
        next_steps = ["补齐题面与必需配置后重新检查 readiness"]
    elif warnings:
        status = "warnings"
        recommendation = "review_warnings"
        next_steps = ["评估并处理 warnings，确认是否允许继续发布"]
    else:
        status = "ready"
        recommendation = "ready_for_release"
        next_steps = ["可以进入构建与发布流程"]
    return {
        "status": status,
        "recommendation": recommendation,
        "next_steps": next_steps,
        "blocking_issue_count": len(blocking_issues),
        "warning_count": len(warnings),
        "error_section_count": len(error_sections),
        "sections_with_errors": error_sections,
    }


def _build_recovery_actions(
    summary: dict[str, Any],
    *,
    problem_id: int,
    testset: str,
) -> list[dict[str, Any]]:
    recommendation = summary["recommendation"]
    if recommendation == "fix_blocking_issues":
        return [
            build_recovery_action(
                action="fix_blocking_issues",
                description="根据 blocking_issues 修复题目配置后重新执行 readiness 检查。",
                tool="check_problem_readiness",
                params={"problem_id": problem_id, "testset": testset},
            )
        ]
    if recommendation == "review_warnings":
        return [
            build_recovery_action(
                action="review_warnings",
                description="确认 warnings 是否需要修复，必要时修复后重新执行 readiness 检查。",
                tool="check_problem_readiness",
                params={"problem_id": problem_id, "testset": testset},
            ),
            build_recovery_action(
                action="continue_release_with_warning_policy",
                description="如果 warnings 可接受，可在发布流程中显式设置 allow_warnings=True。",
                tool="prepare_problem_release",
                params={"problem_id": problem_id, "testset": testset, "allow_warnings": True},
            ),
        ]
    return []


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
    statements: dict[str, Any] = {}
    validator = ""
    checker = ""
    interactor = ""
    extra_validators: list[str] = []
    statement_resource_references: list[str] = []
    source_file_names: set[str] = set()
    resource_file_names: set[str] = set()
    aux_file_names: set[str] = set()
    file_inventory_loaded = False
    info = None

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

    try:
        problems = session.client.get_problems(problem_id=problem_id)
        if not problems:
            raise ValueError(f"无法获取题目 {problem_id} 的元数据")
        details["problem"] = _serialize_problem(problems[0])
    except Exception as exc:
        _append_check_error("题目元数据", exc, blocking_issues, details)

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
                if info is not None and info.interactive and not _has_text(statement.interaction):
                    blocking_issues.append(f"{lang} 题面缺少交互协议（interaction）")
                if info is not None and not info.interactive and _has_text(statement.interaction):
                    warnings.append(f"{lang} 题面设置了 interaction，但当前题目不是交互题")
            statement_resource_references = _extract_statement_resource_references(statements)
            details["statements"]["resource_references"] = statement_resource_references
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

    try:
        interactor = session.get_interactor()
        details["interactor"] = interactor
        if info is not None and info.interactive and not interactor:
            blocking_issues.append("交互题未设置 interactor")
        if info is not None and not info.interactive and interactor:
            warnings.append("当前题目不是交互题，但设置了 interactor")
    except Exception as exc:
        if info is not None and not info.interactive:
            interactor = ""
            details["interactor"] = {
                "status": "ignored",
                "reason": "problem is not interactive",
                "error": str(exc),
            }
        else:
            _append_check_error("interactor", exc, blocking_issues, details)

    details["interaction"] = {
        "interactive": info.interactive if info is not None else None,
        "interaction_languages": sorted(
            lang for lang, statement in statements.items() if _has_text(statement.interaction)
        ),
        "has_interactor": bool(interactor),
        "has_checker": bool(checker),
    }

    try:
        extra_validators = session.get_extra_validators()
        details["extra_validators"] = {
            "count": len(extra_validators),
            "names": extra_validators,
        }
    except Exception as exc:
        _append_check_error("额外 validator", exc, blocking_issues, details)

    try:
        files = session.get_files()
        source_file_names = {file.name for file in files.sourceFiles}
        resource_file_names = {file.name for file in files.resourceFiles}
        aux_file_names = {file.name for file in files.auxFiles}
        missing_references = []
        for source_name, label in (
            (validator, "validator"),
            (checker, "checker"),
        ):
            if source_name and source_name not in source_file_names:
                missing_references.append(f"{label}: {source_name}")
        if info is not None and info.interactive and interactor and interactor not in source_file_names:
            missing_references.append(f"interactor: {interactor}")
        for source_name in extra_validators:
            if source_name not in source_file_names:
                missing_references.append(f"extra validator: {source_name}")

        details["files"] = {
            "resource_count": len(files.resourceFiles),
            "source_count": len(files.sourceFiles),
            "aux_count": len(files.auxFiles),
            "missing_references": missing_references,
        }
        file_inventory_loaded = True
        if missing_references:
            blocking_issues.append(
                "以下已配置源码文件不存在于题目源文件列表中: "
                + ", ".join(missing_references)
            )
    except Exception as exc:
        _append_check_error("题目文件", exc, blocking_issues, details)

    try:
        statement_resources = session.get_statement_resources()
        statement_resource_names = sorted(file.name for file in statement_resources)
        available_statement_resources = set(statement_resource_names) | resource_file_names
        missing_statement_resources = _find_missing_file_references(
            statement_resource_references,
            sorted(available_statement_resources),
        )
        untracked_statement_resources = sorted(
            name for name in statement_resource_names if file_inventory_loaded and name not in resource_file_names
        )
        details["statement_resources"] = {
            "count": len(statement_resource_names),
            "names": statement_resource_names,
            "referenced_names": statement_resource_references,
            "missing_references": missing_statement_resources,
            "untracked_resources": untracked_statement_resources,
        }
        if missing_statement_resources:
            blocking_issues.append(
                "题面引用了不存在的资源文件: " + ", ".join(missing_statement_resources)
            )
        if untracked_statement_resources:
            warnings.append(
                "以下题面资源未出现在 resourceFiles 列表中: "
                + ", ".join(untracked_statement_resources)
            )
    except Exception as exc:
        _append_check_error("题面资源", exc, blocking_issues, details)

    try:
        tests = session.get_tests(testset=testset)
        statement_samples = [test for test in tests if test.useInStatements]
        generated_tests = [test for test in tests if not test.manual]
        samples_missing_input = [
            test.index for test in statement_samples if not _has_text(test.inputForStatement)
        ]
        samples_missing_output = [
            test.index for test in statement_samples if not _has_text(test.outputForStatement)
        ]
        samples_without_verification = [
            test.index
            for test in statement_samples
            if test.verifyInputOutputForStatements is not True
        ]
        tests_with_points = [test.index for test in tests if test.points is not None]
        details["tests"] = {
            "count": len(tests),
            "manual_count": sum(1 for test in tests if test.manual),
            "generated_count": len(generated_tests),
            "sample_count": len(statement_samples),
            "group_names": sorted(
                {
                    group_name
                    for test in tests
                    if (group_name := _normalize_text(test.group)) is not None
                }
            ),
            "samples_missing_input_for_statement": samples_missing_input,
            "samples_missing_output_for_statement": samples_missing_output,
            "samples_without_statement_verification": samples_without_verification,
            "tests_with_points": tests_with_points,
        }
        if not tests:
            blocking_issues.append(f"测试集 {testset} 中没有测试")
        elif not statement_samples:
            warnings.append(f"测试集 {testset} 中没有用于题面的样例")
        if samples_missing_input:
            warnings.append(
                f"以下样例缺少题面输入展示内容: {', '.join(map(str, samples_missing_input))}"
            )
        if samples_missing_output:
            warnings.append(
                f"以下样例缺少题面输出展示内容: {', '.join(map(str, samples_missing_output))}"
            )
        if samples_without_verification:
            warnings.append(
                "以下样例未启用题面输入输出校验: "
                + ", ".join(map(str, samples_without_verification))
            )
        if tests_with_points and statements:
            missing_scoring_languages = [
                lang for lang, statement in statements.items() if not _has_text(statement.scoring)
            ]
            details["statements"]["missing_scoring_languages"] = missing_scoring_languages
            if missing_scoring_languages:
                warnings.append(
                    "题目存在带分测试，但以下题面缺少 scoring 字段: "
                    + ", ".join(missing_scoring_languages)
                )
        if generated_tests:
            script = session.view_script(testset)
            script_text = (
                script.decode("utf-8", errors="ignore") if isinstance(script, bytes) else str(script)
            )
            normalized_script_lines = _normalize_script_lines(script_text)
            generated_without_script_line = [
                test.index for test in generated_tests if not _has_text(test.scriptLine)
            ]
            generated_missing_script_line = [
                test.index
                for test in generated_tests
                if _has_text(test.scriptLine) and test.scriptLine.strip() not in normalized_script_lines
            ]
            referenced_generator_files = sorted(
                {
                    reference
                    for test in generated_tests
                    for reference in _extract_script_related_references(test.scriptLine)
                }
            )
            missing_generator_files = (
                _find_missing_file_references(
                    referenced_generator_files,
                    sorted(source_file_names | resource_file_names | aux_file_names),
                )
                if file_inventory_loaded
                else []
            )
            details["script"] = {
                "generated_test_count": len(generated_tests),
                "present": _has_text(script_text),
                "generated_tests_without_script_line": generated_without_script_line,
                "generated_tests_missing_from_script": generated_missing_script_line,
                "referenced_related_files": referenced_generator_files,
                "missing_related_file_references": missing_generator_files,
            }
            if not _has_text(script_text):
                warnings.append(f"测试集 {testset} 存在生成测试，但生成脚本为空")
            if generated_without_script_line:
                warnings.append(
                    "以下生成测试缺少 scriptLine: "
                    + ", ".join(map(str, generated_without_script_line))
                )
            if generated_missing_script_line:
                warnings.append(
                    "以下生成测试的 scriptLine 未出现在当前生成脚本中: "
                    + ", ".join(map(str, generated_missing_script_line))
                )
            if missing_generator_files:
                warnings.append(
                    "生成测试脚本引用了不存在的相关文件或生成器: "
                    + ", ".join(missing_generator_files)
                )
        group_names = details["tests"]["group_names"]
        if group_names:
            test_groups = session.view_test_groups(testset=testset)
            defined_group_names: set[str] = set()
            duplicate_group_names: set[str] = set()
            undefined_dependencies: list[str] = []
            group_dependencies: dict[str, list[str]] = {}

            for test_group in test_groups:
                group_name = _normalize_text(test_group.name)
                if group_name is None:
                    continue
                if group_name in defined_group_names:
                    duplicate_group_names.add(group_name)
                defined_group_names.add(group_name)

            for test_group in test_groups:
                group_name = _normalize_text(test_group.name)
                if group_name is None:
                    continue
                normalized_dependencies: list[str] = []
                for dependency in test_group.dependencies:
                    dependency_name = _normalize_text(dependency)
                    if dependency_name is None:
                        continue
                    normalized_dependencies.append(dependency_name)
                    if dependency_name not in defined_group_names:
                        undefined_dependencies.append(f"{group_name} -> {dependency_name}")
                group_dependencies[group_name] = normalized_dependencies

            undefined_group_names = sorted(set(group_names) - defined_group_names)
            empty_group_names = sorted(defined_group_names - set(group_names))
            cyclic_dependencies = _find_test_group_cycles(group_dependencies)
            details["test_groups"] = {
                "defined_count": len(test_groups),
                "defined_names": sorted(defined_group_names),
                "undefined_group_names": undefined_group_names,
                "duplicate_group_names": sorted(duplicate_group_names),
                "undefined_dependencies": undefined_dependencies,
                "empty_group_names": empty_group_names,
                "cyclic_dependencies": cyclic_dependencies,
            }
            if undefined_group_names:
                blocking_issues.append(
                    "以下测试引用了未定义的测试组: " + ", ".join(undefined_group_names)
                )
            if duplicate_group_names:
                blocking_issues.append(
                    "以下测试组定义重复: " + ", ".join(sorted(duplicate_group_names))
                )
            if undefined_dependencies:
                blocking_issues.append(
                    "以下测试组依赖了未定义的测试组: " + ", ".join(undefined_dependencies)
                )
            if cyclic_dependencies:
                blocking_issues.append(
                    "以下测试组依赖成环: " + ", ".join(cyclic_dependencies)
                )
            if empty_group_names:
                warnings.append("以下测试组未分配任何测试: " + ", ".join(empty_group_names))
    except Exception as exc:
        _append_check_error("测试", exc, blocking_issues, details)

    try:
        solutions = session.get_solutions()
        accepted_solution_count = sum(
            1 for solution in solutions if solution.tag in (SolutionTag.MA, SolutionTag.OK)
        )
        main_solution_count = sum(1 for solution in solutions if solution.tag == SolutionTag.MA)
        has_main_solution = main_solution_count > 0
        has_non_accepted_solution = any(
            solution.tag not in (SolutionTag.MA, SolutionTag.OK) for solution in solutions
        )
        non_accepted_tag_counts = Counter(
            solution.tag.value
            for solution in solutions
            if solution.tag not in (SolutionTag.MA, SolutionTag.OK)
        )
        details["solutions"] = {
            "count": len(solutions),
            "accepted_count": accepted_solution_count,
            "main_solution_count": main_solution_count,
            "has_main_solution": has_main_solution,
            "has_non_accepted_solution": has_non_accepted_solution,
            "non_accepted_tag_counts": dict(sorted(non_accepted_tag_counts.items())),
        }
        if accepted_solution_count == 0:
            blocking_issues.append("缺少正确解")
        if not has_main_solution:
            warnings.append("缺少主解（MA）")
        if main_solution_count > 1:
            warnings.append(f"主解（MA）数量异常: {main_solution_count}")
        if not has_non_accepted_solution:
            warnings.append("缺少错误解或边界解，校验覆盖可能不足")
        elif len(non_accepted_tag_counts) < 2:
            warnings.append("错误解或边界解类型较少，建议至少覆盖两类非通过判定")
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
        details["general_tutorial"] = {"present": _has_text(tutorial)}
        if not _has_text(tutorial):
            warnings.append("通用题解为空")
    except Exception as exc:
        _append_check_error("通用题解", exc, blocking_issues, details)

    summary = _build_summary(blocking_issues, warnings, details)
    can_retry = summary["status"] != "ready"
    decision = summary["recommendation"]
    return {
        "status": "success",
        "stage": "completed",
        "decision": decision,
        "can_retry": can_retry,
        "recovery_actions": _build_recovery_actions(
            summary,
            problem_id=problem_id,
            testset=testset,
        ),
        "ready": not blocking_issues,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "summary": summary,
        "details": details,
    }
