from typing import Optional

from src.mcp.utils.common import get_problem_session
from src.polygon.models import ProblemInfo

def get_problem_info(problem_id: int, pin: Optional[str] = None) -> ProblemInfo:
    """
    获取Polygon题目的基本信息
    
    Args:
        problem_id: 题目ID
        
    Returns:
        ProblemInfo: 题目的基本信息，包含以下字段：
            - inputFile: 题目的输入文件名
            - outputFile: 题目的输出文件名
            - interactive: 是否为交互题
            - timeLimit: 时间限制（毫秒）
            - memoryLimit: 内存限制（MB）
            
    Raises:
        ValueError: 当环境变量未设置时抛出
    """
    return get_problem_session(problem_id, pin).get_info()
