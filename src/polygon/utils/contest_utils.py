from typing import Dict, Optional
from src.polygon.utils.client_utils import make_api_request

def make_contest_request(
    api_key: str,
    api_secret: str,
    base_url: str,
    method: str,
    contest_id: int,
    pin: Optional[str] = None,
    params: Optional[Dict] = None
):
    """
    发送比赛相关的API请求
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        method: API方法名
        contest_id: 比赛ID
        pin: 比赛的PIN码（如果有）
        params: 额外的请求参数
        
    Returns:
        API响应数据
    """
    if params is None:
        params = {}
        
    # 添加比赛ID和PIN码（如果有）
    params["contestId"] = str(contest_id)
    if pin is not None:
        params["pin"] = pin
        
    return make_api_request(
        api_key, 
        api_secret, 
        base_url, 
        method, 
        params
    ) 