from typing import Optional

from src.mcp.utils.common import call_problem_session_method


def get_problem_checker(problem_id: int, pin: Optional[str] = None) -> str:
    """
    获取Polygon题目当前使用的checker文件名
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: checker文件名
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    return call_problem_session_method(problem_id, pin, "get_checker")
