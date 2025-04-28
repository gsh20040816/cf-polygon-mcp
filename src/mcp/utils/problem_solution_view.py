from typing import Optional
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def view_problem_solution(
    problem_id: int,
    solution_name: str,
    pin: Optional[str] = None
) -> bytes:
    """
    获取Polygon题目中某个解决方案的源代码
    
    Args:
        problem_id: 题目ID
        solution_name: 解决方案文件名
        pin: 题目的PIN码（如果有）
        
    Returns:
        bytes: 解决方案源代码的原始内容
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
        
    Example:
        >>> # 获取并查看解决方案列表
        >>> solutions = get_problem_solutions(12345)
        >>> for solution in solutions:
        >>>     print(f"Solution: {solution.name}")
        >>> 
        >>> # 查看特定解决方案的源代码
        >>> content = view_problem_solution(12345, "main.cpp")
        >>> print(content.decode('utf-8'))
        >>> 
        >>> # 如果题目有PIN码
        >>> content = view_problem_solution(
        >>>     problem_id=12345,
        >>>     solution_name="main.cpp",
        >>>     pin="your_pin_code"
        >>> )
        >>> print(content.decode('utf-8'))
    """
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.view_solution(solution_name) 