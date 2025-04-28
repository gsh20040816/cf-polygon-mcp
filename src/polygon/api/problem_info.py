from src.polygon.models import ProblemInfo
from src.polygon.utils.client_utils import make_api_request

def get_problem_info(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int
) -> ProblemInfo:
    """
    获取题目的基本信息
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        
    Returns:
        ProblemInfo: 题目的基本信息
    """
    params = {
        "problemId": str(problem_id)
    }
    
    response = make_api_request(api_key, api_secret, base_url, "problem.info", params)
    return ProblemInfo.from_dict(response["result"]) 