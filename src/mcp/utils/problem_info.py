from src.polygon.models import ProblemInfo
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def get_problem_info(problem_id: int) -> ProblemInfo:
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
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id)
    return session.get_info() 