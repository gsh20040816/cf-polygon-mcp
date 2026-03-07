from typing import Optional

from src.mcp.utils.common import call_problem_session_method, parse_enum
from src.polygon.models import FileType


def view_problem_file(
    problem_id: int,
    file_type: str,
    file_name: str,
    pin: Optional[str] = None
) -> bytes:
    """
    获取Polygon题目中的文件内容
    
    Args:
        problem_id: 题目ID
        file_type: 文件类型，可选值：
            - resource: 资源文件
            - source: 源代码文件
            - aux: 辅助文件
        file_name: 文件名
        pin: 题目的PIN码（如果有）
        
    Returns:
        bytes: 文件的原始内容
        
    Raises:
        ValueError: 当环境变量未设置时或文件类型无效时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
        
    Example:
        >>> # 查看checker源代码
        >>> content = view_problem_file(12345, "source", "checker.cpp")
        >>> print(content.decode('utf-8'))
        >>> 
        >>> # 查看资源文件
        >>> content = view_problem_file(12345, "resource", "testlib.h")
        >>> print(content.decode('utf-8'))
    """
    file_type_enum = parse_enum(FileType, file_type, "file_type")
    return call_problem_session_method(
        problem_id,
        pin,
        "view_file",
        file_type_enum,
        file_name,
    )
