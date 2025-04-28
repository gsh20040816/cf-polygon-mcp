from typing import Dict, Optional
from src.polygon.models import Statement
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def get_problem_statements(problem_id: int, pin: Optional[str] = None) -> Dict[str, Statement]:
    """
    获取Polygon题目的多语言陈述
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        Dict[str, Statement]: 语言代码到题目陈述的映射，每个Statement包含：
            - encoding: 陈述的编码格式
            - name: 该语言下的题目名称
            - legend: 题目描述
            - input: 输入格式说明
            - output: 输出格式说明
            - scoring: 评分说明（可选）
            - interaction: 交互协议说明（仅用于交互题，可选）
            - notes: 题目注释（可选）
            - tutorial: 题解（可选）
            
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    api_key, api_secret = get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    statements = session.get_statements()
    return statements.items 