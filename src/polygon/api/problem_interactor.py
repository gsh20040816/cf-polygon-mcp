from typing import Optional
from src.polygon.utils.problem_utils import make_problem_request

def get_problem_interactor(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None
) -> str:
    """
    获取当前设置的interactor文件名
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: interactor文件名。如果题目不是交互题，可能返回空字符串
        
    Example:
        >>> interactor_name = get_problem_interactor(api_key, api_secret, base_url, 12345)
        >>> if interactor_name:
        >>>     print(f"Current interactor: {interactor_name}")
        >>> else:
        >>>     print("Not an interactive problem")
    """
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.interactor", problem_id, pin
    )
    return response["result"] 