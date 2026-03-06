from src.polygon.models import Problem
from src.polygon.utils.client_utils import make_api_request


def create_problem(
    api_key: str,
    api_secret: str,
    base_url: str,
    name: str,
) -> Problem:
    """
    创建一个新的空题目。

    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        name: 题目名称

    Returns:
        Problem: 新创建的题目对象
    """
    response = make_api_request(
        api_key,
        api_secret,
        base_url,
        "problem.create",
        {"name": name},
        http_method="POST",
    )
    return Problem.from_dict(response["result"])
