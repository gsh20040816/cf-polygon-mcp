from typing import Optional
from src.polygon.models import ProblemInfo
from src.polygon.utils.problem_utils import make_problem_request, check_write_access
from src.polygon.models import AccessType

def update_problem_info(
    api_key: str,
    api_secret: str, 
    base_url: str,
    problem_id: int,
    pin: Optional[str],
    access_type: AccessType,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    time_limit: Optional[int] = None,
    memory_limit: Optional[int] = None,
    interactive: Optional[bool] = None
) -> dict:
    """
    更新题目信息
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        access_type: 用户对题目的访问权限
        input_file: 输入文件名
        output_file: 输出文件名
        time_limit: 时间限制（毫秒）
        memory_limit: 内存限制（MB）
        interactive: 是否为交互题
        
    Returns:
        ProblemInfo: 更新后的题目信息
    """
    # 检查写入权限
    check_write_access(access_type)
    
    params = {}
    if input_file is not None:
        params["inputFile"] = input_file
    if output_file is not None:
        params["outputFile"] = output_file
    if time_limit is not None:
        params["timeLimit"] = str(time_limit)
    if memory_limit is not None:
        params["memoryLimit"] = str(memory_limit)
    if interactive is not None:
        params["interactive"] = "true" if interactive else "false"
        
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.updateInfo", problem_id, pin, params
    )
    return response 