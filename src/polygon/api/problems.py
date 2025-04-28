from typing import List, Optional
from src.polygon.models import Problem
from src.polygon.utils.client_utils import make_api_request

def get_problems(
    api_key: str,
    api_secret: str,
    base_url: str,
    show_deleted: Optional[bool] = None,
    problem_id: Optional[int] = None,
    name: Optional[str] = None,
    owner: Optional[str] = None
) -> List[Problem]:
    """
    获取用户可访问的题目列表
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        show_deleted: 是否显示已删除的题目（默认为False）
        problem_id: 按题目ID筛选
        name: 按题目名称筛选
        owner: 按题目所有者筛选
        
    Returns:
        List[Problem]: 题目列表
    """
    params = {}
    
    # 添加可选参数
    if show_deleted is not None:
        params["showDeleted"] = "true" if show_deleted else "false"
    if problem_id is not None:
        params["id"] = str(problem_id)
    if name is not None:
        params["name"] = name
    if owner is not None:
        params["owner"] = owner
        
    response = make_api_request(api_key, api_secret, base_url, "problems.list", params)
    return [Problem.from_dict(prob) for prob in response.get("result", [])] 