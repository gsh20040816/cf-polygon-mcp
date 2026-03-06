from __future__ import annotations

from typing import Any, Optional

from src.mcp.utils.common import (
    build_operation_result,
    get_problem_session,
    is_ok_result,
    serialize_problem,
)
from src.mcp.utils.problem_package_workflow import build_problem_package_and_wait
from src.mcp.utils.problem_readiness import check_problem_readiness


def _is_failed_response(result: Any) -> bool:
    return not is_ok_result(result)


def _get_problem_snapshot(session: Any) -> dict[str, Any]:
    problems = session.client.get_problems(problem_id=session.problem_id)
    if not problems:
        raise ValueError(f"无法获取题目 {session.problem_id} 的元数据")
    return serialize_problem(problems[0])


def prepare_problem_release(
    problem_id: int,
    pin: Optional[str] = None,
    testset: str = "tests",
    full: bool = True,
    verify: bool = True,
    timeout_seconds: int = 1800,
    poll_interval_seconds: float = 5.0,
    message: Optional[str] = None,
    minor_changes: Optional[bool] = None,
    allow_warnings: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    """
    按发布流程执行：更新工作副本、检查 readiness、构建并等待、提交修改。
    """
    release_options = {
        "testset": testset,
        "full": full,
        "verify": verify,
        "timeout_seconds": timeout_seconds,
        "poll_interval_seconds": poll_interval_seconds,
        "message": message,
        "minor_changes": minor_changes,
        "allow_warnings": allow_warnings,
        "force": force,
    }
    session = get_problem_session(problem_id, pin)
    update_result = session.update_working_copy()
    if _is_failed_response(update_result):
        return build_operation_result(
            action="prepare_problem_release",
            success=False,
            message="工作副本更新失败，停止发布流程",
            result=update_result,
            problem_id=problem_id,
            pin=pin,
            stage="update_working_copy",
            can_proceed=False,
            decision="update_failed",
            update_result=update_result,
            release_options=release_options,
        )

    readiness = check_problem_readiness(problem_id=problem_id, pin=pin, testset=testset)
    if readiness["blocking_issues"] and not force:
        return build_operation_result(
            action="prepare_problem_release",
            success=False,
            message="发布前检查未通过，存在阻塞问题",
            status_override="blocked",
            problem_id=problem_id,
            pin=pin,
            stage="readiness",
            can_proceed=False,
            decision="blocking_issues",
            update_result=update_result,
            readiness=readiness,
            release_options=release_options,
        )
    if readiness["warnings"] and not allow_warnings and not force:
        return build_operation_result(
            action="prepare_problem_release",
            success=False,
            message="发布前检查包含警告，未允许继续发布",
            status_override="blocked",
            problem_id=problem_id,
            pin=pin,
            stage="readiness",
            can_proceed=False,
            decision="warnings_not_allowed",
            update_result=update_result,
            readiness=readiness,
            release_options=release_options,
        )

    build_result = build_problem_package_and_wait(
        problem_id=problem_id,
        full=full,
        verify=verify,
        pin=pin,
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    if build_result["status"] != "success":
        return build_operation_result(
            action="prepare_problem_release",
            success=False,
            message="题目包未成功构建，停止提交",
            result=build_result,
            problem_id=problem_id,
            pin=pin,
            stage="build",
            can_proceed=False,
            decision="build_failed",
            update_result=update_result,
            readiness=readiness,
            build_result=build_result,
            release_options=release_options,
        )

    release_warnings: list[str] = []
    pre_commit_snapshot = None
    try:
        pre_commit_snapshot = _get_problem_snapshot(session)
    except Exception as exc:
        release_warnings.append(f"提交前题目快照获取失败: {exc}")

    commit_result = session.commit_changes(
        minor_changes=minor_changes,
        message=message,
    )
    if _is_failed_response(commit_result):
        return build_operation_result(
            action="prepare_problem_release",
            success=False,
            message="构建成功，但提交修改失败",
            result=commit_result,
            problem_id=problem_id,
            pin=pin,
            stage="commit",
            can_proceed=False,
            decision="commit_failed",
            update_result=update_result,
            readiness=readiness,
            build_result=build_result,
            commit_result=commit_result,
            pre_commit_snapshot=pre_commit_snapshot,
            release_warnings=release_warnings,
            release_options=release_options,
        )

    post_commit_snapshot = None
    try:
        post_commit_snapshot = _get_problem_snapshot(session)
    except Exception as exc:
        release_warnings.append(f"提交后题目快照获取失败: {exc}")

    if post_commit_snapshot is not None and post_commit_snapshot.get("modified"):
        release_warnings.append("提交后题目仍处于 modified 状态，可能还有未提交改动")

    package_revision = build_result.get("package", {}).get("revision")
    committed_revision = (
        post_commit_snapshot.get("revision") if post_commit_snapshot is not None else None
    )
    if package_revision is not None and committed_revision is not None and package_revision != committed_revision:
        release_warnings.append(
            f"构建包 revision={package_revision}，提交后题目 revision={committed_revision}，请确认发布的是预期版本"
        )

    return build_operation_result(
        action="prepare_problem_release",
        success=True,
        message="题目发布流程已完成",
        result=commit_result,
        problem_id=problem_id,
        pin=pin,
        stage="completed",
        can_proceed=True,
        decision="released",
        update_result=update_result,
        readiness=readiness,
        build_result=build_result,
        commit_result=commit_result,
        release_warnings=release_warnings,
        pre_commit_snapshot=pre_commit_snapshot,
        post_commit_snapshot=post_commit_snapshot,
        release_options=release_options,
    )
