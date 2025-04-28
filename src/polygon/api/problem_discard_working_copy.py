from typing import Optional
from src.polygon.utils.problem_utils import make_problem_request, check_write_access
from src.polygon.models import AccessType

def discard_problem_working_copy(
    api_key: str,
    api_secret: str, 
    base_url: str,
    problem_id: int,
    pin: Optional[str],
    access_type: AccessType
) -> dict:
    """
    丢弃题目工作副本
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        access_type: 用户对题目的访问权限
        
    Returns:
        dict: API响应
    """
    # 检查写入权限
    check_write_access(access_type)
    
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.discardWorkingCopy", problem_id, pin
    )
    
    return response 