from __future__ import annotations

from typing import Any, Optional

from src.mcp.utils.common import get_problem_session
from src.mcp.utils.problem_package_workflow import build_problem_package_and_wait
from src.mcp.utils.problem_readiness import check_problem_readiness


def _is_failed_response(result: Any) -> bool:
    return isinstance(result, dict) and result.get("status") == "FAILED"


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
    session = get_problem_session(problem_id, pin)
    update_result = session.update_working_copy()
    if _is_failed_response(update_result):
        return {
            "status": "error",
            "message": "工作副本更新失败，停止发布流程",
            "update_result": update_result,
        }

    readiness = check_problem_readiness(problem_id=problem_id, pin=pin, testset=testset)
    if readiness["blocking_issues"] and not force:
        return {
            "status": "blocked",
            "message": "发布前检查未通过，存在阻塞问题",
            "update_result": update_result,
            "readiness": readiness,
        }
    if readiness["warnings"] and not allow_warnings and not force:
        return {
            "status": "blocked",
            "message": "发布前检查包含警告，未允许继续发布",
            "update_result": update_result,
            "readiness": readiness,
        }

    build_result = build_problem_package_and_wait(
        problem_id=problem_id,
        full=full,
        verify=verify,
        pin=pin,
        timeout_seconds=timeout_seconds,
        poll_interval_seconds=poll_interval_seconds,
    )
    if build_result["status"] != "success":
        return {
            "status": "error",
            "message": "题目包未成功构建，停止提交",
            "update_result": update_result,
            "readiness": readiness,
            "build_result": build_result,
        }

    commit_result = session.commit_changes(
        minor_changes=minor_changes,
        message=message,
    )
    if _is_failed_response(commit_result):
        return {
            "status": "error",
            "message": "构建成功，但提交修改失败",
            "update_result": update_result,
            "readiness": readiness,
            "build_result": build_result,
            "commit_result": commit_result,
        }

    return {
        "status": "success",
        "message": "题目发布流程已完成",
        "update_result": update_result,
        "readiness": readiness,
        "build_result": build_result,
        "commit_result": commit_result,
    }
