from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def update_problem_working_copy(problem_id: int) -> dict:
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
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id)
    
    result = session.update_working_copy()
    
    if result.get("status") == "OK":
        return {
            "status": "success",
            "message": "工作副本已更新",
            "result": result
        }
    else:
        return {
            "status": "error",
            "message": "工作副本更新失败",
            "result": result
        }
        
def discard_problem_working_copy(problem_id: int) -> dict:
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
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id)
    
    result = session.discard_working_copy()
    
    if result.get("status") == "OK":
        return {
            "status": "success",
            "message": "工作副本已丢弃",
            "result": result
        }
    else:
        return {
            "status": "error",
            "message": "工作副本丢弃失败",
            "result": result
        } 