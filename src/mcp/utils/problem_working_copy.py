from typing import Optional

from src.mcp.utils.common import (
    build_operation_result,
    get_problem_session,
    is_ok_result,
    serialize_problem,
)


def _get_problem_snapshot(session, problem_id: int):
    problems = session.client.get_problems(problem_id=problem_id)
    if not problems:
        return None
    return serialize_problem(problems[0])

def update_problem_working_copy(problem_id: int, pin: Optional[str] = None) -> dict:
    """
    更新Polygon题目的工作副本
    
    Args:
        problem_id: 题目ID
        
    Returns:
        dict: 操作结果
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    try:
        session = get_problem_session(problem_id, pin)
        result = session.update_working_copy()
        success = is_ok_result(result)
        return build_operation_result(
            action="update_problem_working_copy",
            success=success,
            message="工作副本已更新" if success else "工作副本更新失败",
            result=result,
            problem_id=problem_id,
            problem=_get_problem_snapshot(session, problem_id) if success else None,
        )
    except Exception as exc:
        return build_operation_result(
            action="update_problem_working_copy",
            success=False,
            message="工作副本更新失败",
            error=exc,
            problem_id=problem_id,
        )
        
def discard_problem_working_copy(problem_id: int, pin: Optional[str] = None) -> dict:
    """
    丢弃Polygon题目的工作副本
    
    Args:
        problem_id: 题目ID
        
    Returns:
        dict: 操作结果
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    try:
        session = get_problem_session(problem_id, pin)
        result = session.discard_working_copy()
        success = is_ok_result(result)
        return build_operation_result(
            action="discard_problem_working_copy",
            success=success,
            message="工作副本已丢弃" if success else "工作副本丢弃失败",
            result=result,
            problem_id=problem_id,
            problem=_get_problem_snapshot(session, problem_id) if success else None,
        )
    except Exception as exc:
        return build_operation_result(
            action="discard_problem_working_copy",
            success=False,
            message="工作副本丢弃失败",
            error=exc,
            problem_id=problem_id,
        )
