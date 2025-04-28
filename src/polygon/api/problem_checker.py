from typing import Optional
from src.polygon.utils.problem_utils import make_problem_request

def get_problem_checker(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None
) -> str:
    """
    获取当前设置的checker文件名
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: checker文件名
        
    Example:
        >>> checker_name = get_problem_checker(api_key, api_secret, base_url, 12345)
        >>> print(f"Current checker: {checker_name}")
    """
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.checker", problem_id, pin
    )
    return response["result"] 