from typing import Optional
from src.polygon.models import FileType
from src.polygon.utils.problem_utils import make_problem_request

def view_problem_file(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    file_type: FileType,
    name: str,
    pin: Optional[str] = None
) -> bytes:
    """
    获取文件内容
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        file_type: 文件类型（resource/source/aux）
        name: 文件名
        pin: 题目的PIN码（如果有）
        
    Returns:
        bytes: 文件内容的原始数据
        
    Example:
        >>> # 查看checker源代码
        >>> content = view_problem_file(api_key, api_secret, base_url, 12345, FileType.SOURCE, "checker.cpp")
        >>> print(content.decode('utf-8'))
        >>> 
        >>> # 查看资源文件
        >>> content = view_problem_file(api_key, api_secret, base_url, 12345, FileType.RESOURCE, "testlib.h")
        >>> print(content.decode('utf-8'))
    """
    params = {
        "type": file_type.value,
        "name": name
    }
    return make_problem_request(
        api_key, api_secret, base_url,
        "problem.viewFile", problem_id, pin, params, raw_response=True
    ) 