from typing import Optional

from src.mcp.utils.common import get_problem_session

def update_problem_info(
    problem_id: int,
    input_file: Optional[str] = None,
    output_file: Optional[str] = None,
    interactive: Optional[bool] = None,
    time_limit: Optional[int] = None,
    memory_limit: Optional[int] = None,
    pin: Optional[str] = None,
) -> dict:
    """
    更新Polygon题目的基本信息
    
    Args:
        problem_id: 题目ID
        input_file: 题目的输入文件名
        output_file: 题目的输出文件名
        interactive: 是否为交互题
        time_limit: 时间限制（毫秒）
        memory_limit: 内存限制（MB）
        
    Returns:
        dict: 更新后的题目信息
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    result = get_problem_session(problem_id, pin).update_info(
        input_file=input_file,
        output_file=output_file,
        time_limit=time_limit,
        memory_limit=memory_limit,
        interactive=interactive,
    )
    
    if result.get("status") == "OK":
        return {
            "status": "success",
            "message": "题目信息更新成功",
            "result": result,
        }
    else:
        return {
            "status": "error",
            "message": "题目信息更新失败",
            "result": result,
        }
