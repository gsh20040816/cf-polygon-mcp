from typing import Optional

from src.polygon.utils.problem_utils import make_problem_request


def get_problem_extra_validators(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None,
) -> list[str]:
    """
    获取当前设置的额外 validator 文件名列表。

    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）

    Returns:
        list[str]: 额外 validator 文件名列表
    """
    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.extraValidators",
        problem_id,
        pin,
    )
    return list(response["result"])
