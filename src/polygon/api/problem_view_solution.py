from typing import Optional
from src.polygon.utils.problem_utils import make_problem_request

def view_problem_solution(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    name: str,
    pin: Optional[str] = None
) -> bytes:
    """
    获取解决方案源代码
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        name: 解决方案文件名
        pin: 题目的PIN码（如果有）
        
    Returns:
        bytes: 解决方案源代码的原始内容
        
    Example:
        >>> # 查看主要解法的源代码
        >>> content = view_problem_solution(api_key, api_secret, base_url, 12345, "main.cpp")
        >>> print(content.decode('utf-8'))
        >>> 
        >>> # 查看错误解法的源代码
        >>> content = view_problem_solution(api_key, api_secret, base_url, 12345, "wrong_answer.py")
        >>> print(content.decode('utf-8'))
    """
    params = {
        "name": name
    }
    return make_problem_request(
        api_key, api_secret, base_url,
        "problem.viewSolution", problem_id, pin, params, raw_response=True
    ) 