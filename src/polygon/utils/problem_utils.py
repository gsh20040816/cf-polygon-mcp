from typing import Dict, Optional
from src.polygon.utils.client_utils import make_api_request
from src.polygon.models import FileType, AccessDeniedException, AccessType

def make_problem_request(
    api_key: str,
    api_secret: str,
    base_url: str,
    method: str,
    problem_id: int,
    pin: Optional[str] = None,
    params: Optional[Dict] = None,
    raw_response: bool = False
):
    """
    发送题目相关的API请求
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        method: API方法名
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        params: 额外的请求参数
        raw_response: 是否返回原始响应内容
        
    Returns:
        API响应数据
    """
    if params is None:
        params = {}
        
    # 添加题目ID和PIN码（如果有）
    params["problemId"] = str(problem_id)
    if pin is not None:
        params["pin"] = pin
        
    return make_api_request(
        api_key, 
        api_secret, 
        base_url, 
        method, 
        params, 
        raw_response
    )

def check_write_access(access_type: AccessType):
    """
    检查是否有写入权限
    
    Args:
        access_type: 访问权限类型
        
    Raises:
        AccessDeniedException: 当权限不足时抛出
    """
    if access_type == AccessType.READ:
        raise AccessDeniedException("需要WRITE或OWNER权限才能执行此操作") 