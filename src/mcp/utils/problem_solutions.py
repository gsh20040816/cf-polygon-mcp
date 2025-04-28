from typing import List, Optional
from src.polygon.models import Solution
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def get_problem_solutions(problem_id: int, pin: Optional[str] = None) -> List[Solution]:
    """
    获取Polygon题目的所有解决方案
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        List[Solution]: 解决方案列表，每个Solution包含：
            - name: 文件名
            - modificationTimeSeconds: 修改时间
            - length: 文件长度
            - tag: 解法标签，可能的值：
                - MA: 主要解法（Main solution）
                - OK: 正确解法（Accepted）
                - RJ: 会被评测系统拒绝的解法（Rejected）
                - TL: 超时解法（Time Limit Exceeded）
                - TO: 解法可能超时也可能通过（Time limit exceeded OR Accepted）
                - WA: 错误答案解法（Wrong Answer）
                - PE: 格式错误解法（Presentation Error）
                - ML: 超内存解法（Memory Limit Exceeded）
                - RE: 运行时错误解法（Runtime Error）
            
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
        
    Example:
        >>> solutions = get_problem_solutions(12345)
        >>> for solution in solutions:
        >>>     print(f"Solution: {solution.name}")
        >>>     print(f"Expected verdict: {solution.get_verdict()}")
        >>>     if solution.is_correct():
        >>>         print("This is a correct solution")
        >>>     elif solution.is_uncertain():
        >>>         print("This solution might be correct or might exceed time limit")
    """
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.get_solutions() 