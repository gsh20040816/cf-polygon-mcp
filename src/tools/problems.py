from typing import List, Optional, Dict
from ..polygon.client import PolygonClient
from ..polygon.models import Problem, ProblemInfo, Statement, LanguageMap

def get_polygon_problems(
    api_key: str,
    api_secret: str,
    show_deleted: Optional[bool] = None,
    problem_id: Optional[int] = None,
    name: Optional[str] = None,
    owner: Optional[str] = None
) -> List[Problem]:
    """
    获取Polygon中的题目列表
    
    Args:
        api_key: Polygon API密钥
        api_secret: Polygon API密钥对应的secret
        show_deleted: 是否显示已删除的题目（默认为False）
        problem_id: 按题目ID筛选
        name: 按题目名称筛选
        owner: 按题目所有者筛选
        
    Returns:
        List[Problem]: 题目列表
    """
    client = PolygonClient(api_key, api_secret)
    return client.get_problems(
        show_deleted=show_deleted,
        problem_id=problem_id,
        name=name,
        owner=owner
    )

def get_polygon_problem_info(api_key: str, api_secret: str, problem_id: int) -> ProblemInfo:
    """
    获取Polygon中特定题目的基本信息
    
    Args:
        api_key: Polygon API密钥
        api_secret: Polygon API密钥对应的secret
        problem_id: 题目ID
        
    Returns:
        ProblemInfo: 题目的基本信息
    """
    client = PolygonClient(api_key, api_secret)
    return client.get_problem_info(problem_id)

def get_polygon_problem_statements(
    api_key: str,
    api_secret: str,
    problem_id: int,
    pin: Optional[str] = None
) -> Dict[str, Statement]:
    """
    获取Polygon中特定题目的多语言陈述
    
    Args:
        api_key: Polygon API密钥
        api_secret: Polygon API密钥对应的secret
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        Dict[str, Statement]: 语言代码到题目陈述的映射
    """
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    statements = session.get_statements()
    return statements.items
