from src.mcp.utils.common import get_client
from src.polygon.models import Problem


def create_problem(name: str) -> Problem:
    """
    创建一个新的空 Polygon 题目。

    Args:
        name: 题目名称

    Returns:
        Problem: 新创建的题目对象
    """
    return get_client().create_problem(name)
