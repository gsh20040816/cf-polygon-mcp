from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from src.mcp.utils.contest_problems import get_contest_problems
from src.mcp.utils.downloads import (
    download_contest_descriptor,
    download_contest_descriptor_info,
    download_contest_statements_pdf,
    download_contest_statements_pdf_info,
    download_problem_descriptor,
    download_problem_descriptor_info,
    download_problem_package_by_url,
    download_problem_package_info_by_url,
)
from src.mcp.utils.problem_checker import get_problem_checker
from src.mcp.utils.problem_content import (
    get_problem_files,
    get_problem_statement_resources,
    get_problem_tags,
    save_problem_file,
    save_problem_general_description,
    save_problem_general_tutorial,
    save_problem_script,
    save_problem_statement_resource,
    save_problem_tags,
    view_problem_general_description,
    view_problem_general_tutorial,
    view_problem_script,
)
from src.mcp.utils.problem_create import create_problem
from src.mcp.utils.problem_extra_validators import get_problem_extra_validators
from src.mcp.utils.problem_file import view_problem_file
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_interactor import get_problem_interactor
from src.mcp.utils.problem_package_workflow import build_problem_package_and_wait
from src.mcp.utils.problem_packages import (
    build_problem_package,
    commit_problem_changes,
    download_problem_package,
    get_problem_packages,
)
from src.mcp.utils.problem_readiness import check_problem_readiness
from src.mcp.utils.problem_release import prepare_problem_release
from src.mcp.utils.problem_save_statement import save_problem_statement
from src.mcp.utils.problem_solution_view import view_problem_solution
from src.mcp.utils.problem_solutions import get_problem_solutions
from src.mcp.utils.problem_sources import (
    edit_problem_solution_extra_tags,
    save_problem_solution,
    set_problem_checker,
    set_problem_interactor,
    set_problem_validator,
)
from src.mcp.utils.problem_statements import get_problem_statements
from src.mcp.utils.problem_tests_extended import (
    enable_problem_groups,
    enable_problem_points,
    get_problem_checker_tests,
    get_problem_tests,
    get_problem_validator_tests,
    save_problem_checker_test,
    save_problem_test,
    save_problem_test_group,
    save_problem_validator_test,
    set_problem_test_group,
    view_problem_test_answer,
    view_problem_test_groups,
    view_problem_test_input,
)
from src.mcp.utils.problem_update_info import update_problem_info
from src.mcp.utils.problem_validator import get_problem_validator
from src.mcp.utils.problem_working_copy import (
    discard_problem_working_copy,
    update_problem_working_copy,
)
from src.mcp.utils.problems import get_problems

ToolCallable = Callable[..., object]


@dataclass(frozen=True)
class ToolRegistration:
    category: str
    func: ToolCallable

    @property
    def name(self) -> str:
        return self.func.__name__


TOOL_REGISTRY: tuple[ToolRegistration, ...] = (
    ToolRegistration("downloads", download_problem_package_by_url),
    ToolRegistration("downloads", download_problem_package_info_by_url),
    ToolRegistration("downloads", download_problem_descriptor),
    ToolRegistration("downloads", download_problem_descriptor_info),
    ToolRegistration("downloads", download_contest_descriptor),
    ToolRegistration("downloads", download_contest_descriptor_info),
    ToolRegistration("downloads", download_contest_statements_pdf),
    ToolRegistration("downloads", download_contest_statements_pdf_info),
    ToolRegistration("read", get_problems),
    ToolRegistration("read", get_problem_info),
    ToolRegistration("read", get_problem_statements),
    ToolRegistration("read", get_problem_statement_resources),
    ToolRegistration("read", get_problem_checker),
    ToolRegistration("read", get_problem_validator),
    ToolRegistration("read", get_problem_extra_validators),
    ToolRegistration("read", get_problem_interactor),
    ToolRegistration("read", get_problem_files),
    ToolRegistration("read", view_problem_file),
    ToolRegistration("read", view_problem_script),
    ToolRegistration("read", get_problem_tests),
    ToolRegistration("read", view_problem_test_input),
    ToolRegistration("read", view_problem_test_answer),
    ToolRegistration("read", get_problem_validator_tests),
    ToolRegistration("read", get_problem_checker_tests),
    ToolRegistration("read", view_problem_test_groups),
    ToolRegistration("read", get_problem_solutions),
    ToolRegistration("read", view_problem_solution),
    ToolRegistration("read", get_problem_tags),
    ToolRegistration("read", view_problem_general_description),
    ToolRegistration("read", view_problem_general_tutorial),
    ToolRegistration("read", get_problem_packages),
    ToolRegistration("read", download_problem_package),
    ToolRegistration("read", get_contest_problems),
    ToolRegistration("write", create_problem),
    ToolRegistration("write", save_problem_statement_resource),
    ToolRegistration("write", set_problem_checker),
    ToolRegistration("write", set_problem_validator),
    ToolRegistration("write", set_problem_interactor),
    ToolRegistration("write", save_problem_file),
    ToolRegistration("write", save_problem_script),
    ToolRegistration("write", save_problem_test),
    ToolRegistration("write", save_problem_validator_test),
    ToolRegistration("write", save_problem_checker_test),
    ToolRegistration("write", save_problem_test_group),
    ToolRegistration("write", set_problem_test_group),
    ToolRegistration("write", enable_problem_groups),
    ToolRegistration("write", enable_problem_points),
    ToolRegistration("write", save_problem_solution),
    ToolRegistration("write", edit_problem_solution_extra_tags),
    ToolRegistration("write", save_problem_tags),
    ToolRegistration("write", save_problem_general_description),
    ToolRegistration("write", save_problem_general_tutorial),
    ToolRegistration("write", build_problem_package),
    ToolRegistration("write", update_problem_info),
    ToolRegistration("write", update_problem_working_copy),
    ToolRegistration("write", commit_problem_changes),
    ToolRegistration("write", discard_problem_working_copy),
    ToolRegistration("write", save_problem_statement),
    ToolRegistration("workflow", build_problem_package_and_wait),
    ToolRegistration("workflow", check_problem_readiness),
    ToolRegistration("workflow", prepare_problem_release),
)


def iter_tool_registrations() -> Iterable[ToolRegistration]:
    return iter(TOOL_REGISTRY)


def get_registered_tool_names() -> list[str]:
    return [registration.name for registration in TOOL_REGISTRY]


def get_registered_tools_by_category() -> dict[str, list[ToolCallable]]:
    grouped: dict[str, list[ToolCallable]] = {}
    for registration in TOOL_REGISTRY:
        grouped.setdefault(registration.category, []).append(registration.func)
    return grouped


def validate_tool_registry() -> None:
    duplicate_names = sorted(
        {
            registration.name
            for registration in TOOL_REGISTRY
            if get_registered_tool_names().count(registration.name) > 1
        }
    )
    if duplicate_names:
        raise ValueError(f"工具注册表存在重复名称: {', '.join(duplicate_names)}")

    invalid_categories = sorted(
        {
            registration.category
            for registration in TOOL_REGISTRY
            if registration.category not in {"read", "write", "workflow", "downloads"}
        }
    )
    if invalid_categories:
        raise ValueError(f"工具注册表存在未知分组: {', '.join(invalid_categories)}")

    non_callables = [
        registration.name for registration in TOOL_REGISTRY if not callable(registration.func)
    ]
    if non_callables:
        raise ValueError(f"工具注册表包含不可调用对象: {', '.join(non_callables)}")
