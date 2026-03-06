from typing import Optional

from src.mcp.utils.common import get_problem_session, parse_enum
from src.polygon.models import (
    File,
    FileType,
    ProblemFiles,
    ResourceAsset,
    ResourceStage,
    SourceType,
)


def get_problem_statement_resources(problem_id: int, pin: Optional[str] = None) -> list[File]:
    """获取题目陈述引用的资源文件列表。"""
    return get_problem_session(problem_id, pin).get_statement_resources()


def save_problem_statement_resource(
    problem_id: int,
    name: str,
    file_content: str,
    pin: Optional[str] = None,
    check_existing: Optional[bool] = None,
):
    """保存题目陈述资源文件。"""
    return get_problem_session(problem_id, pin).save_statement_resource(
        name=name,
        file_content=file_content,
        check_existing=check_existing,
    )


def get_problem_files(problem_id: int, pin: Optional[str] = None) -> ProblemFiles:
    """获取题目的资源文件、源文件和辅助文件列表。"""
    return get_problem_session(problem_id, pin).get_files()


def save_problem_file(
    problem_id: int,
    file_type: str,
    file_name: str,
    file_content: str,
    pin: Optional[str] = None,
    source_type: Optional[str] = None,
    for_types: Optional[str] = None,
    stages: Optional[list[str]] = None,
    assets: Optional[list[str]] = None,
    check_existing: Optional[bool] = None,
):
    """保存题目文件。"""
    file_type_enum = parse_enum(FileType, file_type, "file_type")
    source_type_enum = (
        parse_enum(SourceType, source_type, "source_type") if source_type is not None else None
    )
    stage_values = (
        [parse_enum(ResourceStage, stage, "stage").value for stage in stages]
        if stages is not None
        else None
    )
    asset_values = (
        [parse_enum(ResourceAsset, asset, "asset").value for asset in assets]
        if assets is not None
        else None
    )

    return get_problem_session(problem_id, pin).save_file(
        file_type=file_type_enum,
        name=file_name,
        file_content=file_content,
        source_type=source_type_enum,
        for_types=for_types,
        stages=stage_values,
        assets=asset_values,
        check_existing=check_existing,
    )


def view_problem_script(
    problem_id: int,
    testset: str,
    pin: Optional[str] = None,
) -> bytes:
    """查看题目的测试生成脚本。"""
    return get_problem_session(problem_id, pin).view_script(testset)


def save_problem_script(
    problem_id: int,
    testset: str,
    source: str,
    pin: Optional[str] = None,
):
    """保存题目的测试生成脚本。"""
    return get_problem_session(problem_id, pin).save_script(testset=testset, source=source)


def get_problem_tags(problem_id: int, pin: Optional[str] = None) -> list[str]:
    """获取题目标签列表。"""
    return get_problem_session(problem_id, pin).get_tags()


def save_problem_tags(
    problem_id: int,
    tags: list[str],
    pin: Optional[str] = None,
):
    """保存题目标签列表。"""
    return get_problem_session(problem_id, pin).save_tags(tags)


def view_problem_general_description(problem_id: int, pin: Optional[str] = None) -> str:
    """获取题目的通用描述。"""
    return get_problem_session(problem_id, pin).get_general_description()


def save_problem_general_description(
    problem_id: int,
    description: str,
    pin: Optional[str] = None,
):
    """保存题目的通用描述。"""
    return get_problem_session(problem_id, pin).save_general_description(description)


def view_problem_general_tutorial(problem_id: int, pin: Optional[str] = None) -> str:
    """获取题目的通用题解。"""
    return get_problem_session(problem_id, pin).get_general_tutorial()


def save_problem_general_tutorial(
    problem_id: int,
    tutorial: str,
    pin: Optional[str] = None,
):
    """保存题目的通用题解。"""
    return get_problem_session(problem_id, pin).save_general_tutorial(tutorial)
