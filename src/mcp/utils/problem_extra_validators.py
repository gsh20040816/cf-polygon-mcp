from typing import Optional

from src.mcp.utils.common import call_problem_session_method


def get_problem_extra_validators(problem_id: int, pin: Optional[str] = None) -> list[str]:
    """
    获取 Polygon 题目当前设置的额外 validator 文件名列表。

    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）

    Returns:
        list[str]: 额外 validator 文件名列表

    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    return call_problem_session_method(problem_id, pin, "get_extra_validators")
