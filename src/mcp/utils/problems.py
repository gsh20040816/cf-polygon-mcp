from typing import List, Optional

from src.mcp.utils.common import call_client_method
from src.polygon.models import Problem


def get_problems(
    show_deleted: Optional[bool] = None,
    problem_id: Optional[int] = None,
    name: Optional[str] = None,
    owner: Optional[str] = None
) -> List[Problem]:
    """
    获取Polygon中用户的题目列表
    
    Args:
        show_deleted: 是否显示已删除的题目（默认为False）
        problem_id: 按题目ID筛选
        name: 按题目名称筛选
        owner: 按题目所有者筛选
        
    Returns:
        List[Problem]: 题目列表
        
    Raises:
        ValueError: 当环境变量未设置时抛出
    """
    return call_client_method(
        "get_problems",
        show_deleted=show_deleted,
        problem_id=problem_id,
        name=name,
        owner=owner,
    )
