from typing import Optional

from src.mcp.utils.common import get_problem_session

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
    result = get_problem_session(problem_id, pin).update_working_copy()
    
    if result.get("status") == "OK":
        return {
            "status": "success",
            "message": "工作副本已更新",
            "result": result,
        }
    else:
        return {
            "status": "error",
            "message": "工作副本更新失败",
            "result": result,
        }
        
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
    result = get_problem_session(problem_id, pin).discard_working_copy()
    
    if result.get("status") == "OK":
        return {
            "status": "success",
            "message": "工作副本已丢弃",
            "result": result,
        }
    else:
        return {
            "status": "error",
            "message": "工作副本丢弃失败",
            "result": result,
        }
