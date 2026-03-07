from typing import Optional

from src.mcp.utils.common import (
    call_problem_session_method,
    get_problem_session,
    parse_enum,
    resolve_text_input,
    resolve_upload_name,
    run_write_operation,
)
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
    return call_problem_session_method(problem_id, pin, "get_statement_resources")


def save_problem_statement_resource(
    problem_id: int,
    name: Optional[str] = None,
    file_content: Optional[str] = None,
    pin: Optional[str] = None,
    check_existing: Optional[bool] = None,
    local_path: Optional[str] = None,
):
    """保存题目陈述资源文件。"""
    return run_write_operation(
        action="save_problem_statement_resource",
        success_message="题目陈述资源文件已保存",
        failure_message="题目陈述资源文件保存失败",
        operation=lambda: _save_problem_statement_resource(
            problem_id=problem_id,
            pin=pin,
            name=name,
            file_content=file_content,
            check_existing=check_existing,
            local_path=local_path,
        ),
        problem_id=problem_id,
        name=name,
        local_path=local_path,
        check_existing=check_existing,
    )


def get_problem_files(problem_id: int, pin: Optional[str] = None) -> ProblemFiles:
    """获取题目的资源文件、源文件和辅助文件列表。"""
    return call_problem_session_method(problem_id, pin, "get_files")


def save_problem_file(
    problem_id: int,
    file_type: str,
    file_name: Optional[str] = None,
    file_content: Optional[str] = None,
    pin: Optional[str] = None,
    source_type: Optional[str] = None,
    for_types: Optional[str] = None,
    stages: Optional[list[str]] = None,
    assets: Optional[list[str]] = None,
    check_existing: Optional[bool] = None,
    local_path: Optional[str] = None,
):
    """保存题目文件。"""
    return run_write_operation(
        action="save_problem_file",
        success_message="题目文件已保存",
        failure_message="题目文件保存失败",
        operation=lambda: _save_problem_file(
            problem_id=problem_id,
            pin=pin,
            file_type=file_type,
            file_name=file_name,
            file_content=file_content,
            source_type=source_type,
            for_types=for_types,
            stages=stages,
            assets=assets,
            check_existing=check_existing,
            local_path=local_path,
        ),
        problem_id=problem_id,
        file_type=file_type,
        file_name=file_name,
        local_path=local_path,
        source_type=source_type,
        for_types=for_types,
        stages=stages,
        assets=assets,
        check_existing=check_existing,
    )


def view_problem_script(
    problem_id: int,
    testset: str,
    pin: Optional[str] = None,
) -> bytes:
    """查看题目的测试生成脚本。"""
    return call_problem_session_method(problem_id, pin, "view_script", testset)


def save_problem_script(
    problem_id: int,
    testset: str,
    source: Optional[str] = None,
    pin: Optional[str] = None,
    local_path: Optional[str] = None,
):
    """保存题目的测试生成脚本。"""
    return run_write_operation(
        action="save_problem_script",
        success_message="题目测试生成脚本已保存",
        failure_message="题目测试生成脚本保存失败",
        operation=lambda: _save_problem_script(
            problem_id=problem_id,
            testset=testset,
            pin=pin,
            source=source,
            local_path=local_path,
        ),
        problem_id=problem_id,
        testset=testset,
        local_path=local_path,
    )


def get_problem_tags(problem_id: int, pin: Optional[str] = None) -> list[str]:
    """获取题目标签列表。"""
    return call_problem_session_method(problem_id, pin, "get_tags")


def save_problem_tags(
    problem_id: int,
    tags: list[str],
    pin: Optional[str] = None,
):
    """保存题目标签列表。"""
    return run_write_operation(
        action="save_problem_tags",
        success_message="题目标签已保存",
        failure_message="题目标签保存失败",
        operation=lambda: get_problem_session(problem_id, pin).save_tags(tags),
        problem_id=problem_id,
        tags=tags,
    )


def view_problem_general_description(problem_id: int, pin: Optional[str] = None) -> str:
    """获取题目的通用描述。"""
    return call_problem_session_method(problem_id, pin, "get_general_description")


def save_problem_general_description(
    problem_id: int,
    description: str,
    pin: Optional[str] = None,
):
    """保存题目的通用描述。"""
    return run_write_operation(
        action="save_problem_general_description",
        success_message="题目通用描述已保存",
        failure_message="题目通用描述保存失败",
        operation=lambda: get_problem_session(problem_id, pin).save_general_description(description),
        problem_id=problem_id,
    )


def view_problem_general_tutorial(problem_id: int, pin: Optional[str] = None) -> str:
    """获取题目的通用题解。"""
    return call_problem_session_method(problem_id, pin, "get_general_tutorial")


def save_problem_general_tutorial(
    problem_id: int,
    tutorial: str,
    pin: Optional[str] = None,
):
    """保存题目的通用题解。"""
    return run_write_operation(
        action="save_problem_general_tutorial",
        success_message="题目通用题解已保存",
        failure_message="题目通用题解保存失败",
        operation=lambda: get_problem_session(problem_id, pin).save_general_tutorial(tutorial),
        problem_id=problem_id,
    )


def _save_problem_statement_resource(
    *,
    problem_id: int,
    pin: Optional[str],
    name: Optional[str],
    file_content: Optional[str],
    check_existing: Optional[bool],
    local_path: Optional[str],
):
    resolved_name = resolve_upload_name(name, local_path, "name")
    resolved_content = resolve_text_input(file_content, local_path, "file_content")
    return get_problem_session(problem_id, pin).save_statement_resource(
        name=resolved_name,
        file_content=resolved_content,
        check_existing=check_existing,
    )


def _save_problem_file(
    *,
    problem_id: int,
    pin: Optional[str],
    file_type: str,
    file_name: Optional[str],
    file_content: Optional[str],
    source_type: Optional[str],
    for_types: Optional[str],
    stages: Optional[list[str]],
    assets: Optional[list[str]],
    check_existing: Optional[bool],
    local_path: Optional[str],
):
    file_type_enum = parse_enum(FileType, file_type, "file_type")
    resolved_name = resolve_upload_name(file_name, local_path, "file_name")
    resolved_content = resolve_text_input(file_content, local_path, "file_content")
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
        name=resolved_name,
        file_content=resolved_content,
        source_type=source_type_enum,
        for_types=for_types,
        stages=stage_values,
        assets=asset_values,
        check_existing=check_existing,
    )


def _save_problem_script(
    *,
    problem_id: int,
    testset: str,
    pin: Optional[str],
    source: Optional[str],
    local_path: Optional[str],
):
    resolved_source = resolve_text_input(source, local_path, "source")
    return get_problem_session(problem_id, pin).save_script(
        testset=testset,
        source=resolved_source,
    )
