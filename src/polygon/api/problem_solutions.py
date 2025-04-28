from typing import List, Optional
from src.polygon.models import Solution
from src.polygon.utils.problem_utils import make_problem_request

def get_problem_solutions(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None
) -> List[Solution]:
    """
    获取题目的所有解决方案
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        List[Solution]: 解决方案列表，每个解决方案包含：
            - name: 文件名
            - modificationTimeSeconds: 修改时间
            - length: 文件长度
            - tag: 解法标签（main/ok/wa/tl等）
            
    Example:
        >>> solutions = get_problem_solutions(api_key, api_secret, base_url, 12345)
        >>> for solution in solutions:
        >>>     print(f"Solution: {solution.name}")
        >>>     print(f"Type: {solution.get_verdict()}")
        >>>     if solution.is_correct():
        >>>         print("This is a correct solution")
    """
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.solutions", problem_id, pin
    )
    return [Solution.from_dict(sol) for sol in response["result"]] 