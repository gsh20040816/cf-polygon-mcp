from typing import Optional

from src.mcp.utils.common import (
    get_problem_session,
    parse_enum,
    resolve_text_input,
    resolve_upload_name,
)
from src.polygon.models import SolutionTag, SourceType


def set_problem_validator(
    problem_id: int,
    validator: str,
    pin: Optional[str] = None,
):
    """设置题目的 validator 源文件。"""
    return get_problem_session(problem_id, pin).set_validator(validator)


def set_problem_checker(
    problem_id: int,
    checker: str,
    pin: Optional[str] = None,
):
    """设置题目的 checker 源文件。"""
    return get_problem_session(problem_id, pin).set_checker(checker)


def set_problem_interactor(
    problem_id: int,
    interactor: str,
    pin: Optional[str] = None,
):
    """设置题目的 interactor 源文件。"""
    return get_problem_session(problem_id, pin).set_interactor(interactor)


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
    resolved_name = resolve_upload_name(name, local_path, "name")
    resolved_content = resolve_text_input(file_content, local_path, "file_content")
    source_type_enum = (
        parse_enum(SourceType, source_type, "source_type") if source_type is not None else None
    )
    tag_enum = parse_enum(SolutionTag, tag, "tag") if tag is not None else None
    return get_problem_session(problem_id, pin).save_solution(
        name=resolved_name,
        file_content=resolved_content,
        source_type=source_type_enum,
        tag=tag_enum,
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
    tag_enum = parse_enum(SolutionTag, tag, "tag") if tag is not None else None
    return get_problem_session(problem_id, pin).edit_solution_extra_tags(
        name=name,
        remove=remove,
        testset=testset,
        test_group=test_group,
        tag=tag_enum,
    )
