from typing import Optional

from src.mcp.utils.common import (
    get_problem_session,
    parse_enum,
    resolve_text_input,
    resolve_upload_name,
    run_write_operation,
)
from src.polygon.models import SolutionTag, SourceType


def set_problem_validator(
    problem_id: int,
    validator: str,
    pin: Optional[str] = None,
):
    """设置题目的 validator 源文件。"""
    return run_write_operation(
        action="set_problem_validator",
        success_message="题目 validator 已设置",
        failure_message="题目 validator 设置失败",
        operation=lambda: get_problem_session(problem_id, pin).set_validator(validator),
        problem_id=problem_id,
        validator=validator,
    )


def set_problem_checker(
    problem_id: int,
    checker: str,
    pin: Optional[str] = None,
):
    """设置题目的 checker 源文件。"""
    return run_write_operation(
        action="set_problem_checker",
        success_message="题目 checker 已设置",
        failure_message="题目 checker 设置失败",
        operation=lambda: get_problem_session(problem_id, pin).set_checker(checker),
        problem_id=problem_id,
        checker=checker,
    )


def set_problem_interactor(
    problem_id: int,
    interactor: str,
    pin: Optional[str] = None,
):
    """设置题目的 interactor 源文件。"""
    return run_write_operation(
        action="set_problem_interactor",
        success_message="题目 interactor 已设置",
        failure_message="题目 interactor 设置失败",
        operation=lambda: get_problem_session(problem_id, pin).set_interactor(interactor),
        problem_id=problem_id,
        interactor=interactor,
    )


def save_problem_solution(
    problem_id: int,
    name: Optional[str] = None,
    file_content: Optional[str] = None,
    pin: Optional[str] = None,
    source_type: Optional[str] = None,
    tag: Optional[str] = None,
    check_existing: Optional[bool] = None,
    local_path: Optional[str] = None,
):
    """保存题目解法文件。"""
    return run_write_operation(
        action="save_problem_solution",
        success_message="题目解法文件已保存",
        failure_message="题目解法文件保存失败",
        operation=lambda: _save_problem_solution(
            problem_id=problem_id,
            pin=pin,
            name=name,
            file_content=file_content,
            source_type=source_type,
            tag=tag,
            check_existing=check_existing,
            local_path=local_path,
        ),
        problem_id=problem_id,
        name=name,
        local_path=local_path,
        tag=tag,
        check_existing=check_existing,
    )


def edit_problem_solution_extra_tags(
    problem_id: int,
    name: str,
    remove: bool,
    pin: Optional[str] = None,
    testset: Optional[str] = None,
    test_group: Optional[str] = None,
    tag: Optional[str] = None,
):
    """增删解法的附加标签。"""
    return run_write_operation(
        action="edit_problem_solution_extra_tags",
        success_message="解法附加标签已更新",
        failure_message="解法附加标签更新失败",
        operation=lambda: _edit_problem_solution_extra_tags(
            problem_id=problem_id,
            pin=pin,
            name=name,
            remove=remove,
            testset=testset,
            test_group=test_group,
            tag=tag,
        ),
        problem_id=problem_id,
        name=name,
        remove=remove,
        testset=testset,
        test_group=test_group,
        tag=tag,
    )


def _save_problem_solution(
    *,
    problem_id: int,
    pin: Optional[str],
    name: Optional[str],
    file_content: Optional[str],
    source_type: Optional[str],
    tag: Optional[str],
    check_existing: Optional[bool],
    local_path: Optional[str],
):
    resolved_name = resolve_upload_name(name, local_path, "name")
    resolved_content = resolve_text_input(file_content, local_path, "file_content")
    source_type_enum = None
    if source_type is not None:
        parsed_source_type = parse_enum(SourceType, source_type, "source_type")
        if parsed_source_type != SourceType.SOLUTION:
            raise ValueError("save_problem_solution 只支持 solution 类型，source_type 可省略")
    tag_enum = parse_enum(SolutionTag, tag, "tag") if tag is not None else None
    return get_problem_session(problem_id, pin).save_solution(
        name=resolved_name,
        file_content=resolved_content,
        source_type=source_type_enum,
        tag=tag_enum,
        check_existing=check_existing,
    )


def _edit_problem_solution_extra_tags(
    *,
    problem_id: int,
    pin: Optional[str],
    name: str,
    remove: bool,
    testset: Optional[str],
    test_group: Optional[str],
    tag: Optional[str],
):
    tag_enum = parse_enum(SolutionTag, tag, "tag") if tag is not None else None
    return get_problem_session(problem_id, pin).edit_solution_extra_tags(
        name=name,
        remove=remove,
        testset=testset,
        test_group=test_group,
        tag=tag_enum,
    )
