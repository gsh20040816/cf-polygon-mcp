from mcp.server.fastmcp import FastMCP
from src.tools.problems import get_polygon_problems, get_polygon_problem_info
from typing import List, Optional, Dict
from src.polygon.models import Problem, ProblemInfo, Statement, LanguageMap, FileType
from src.polygon.client import PolygonClient
import os

# Create an MCP server
mcp = FastMCP("CF-Polygon-MCP")

def _get_api_credentials() -> tuple[str, str]:
    """获取API凭证"""
    api_key = os.getenv("POLYGON_API_KEY")
    api_secret = os.getenv("POLYGON_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "请设置环境变量 POLYGON_API_KEY 和 POLYGON_API_SECRET\n"
            "可以通过以下方式设置:\n"
            "export POLYGON_API_KEY=your_key\n"
            "export POLYGON_API_SECRET=your_secret"
        )
    
    return api_key, api_secret

@mcp.tool()
def get_problems(
    show_deleted: Optional[bool] = None,
    problem_id: Optional[int] = None,
    name: Optional[str] = None,
    owner: Optional[str] = None
) -> List[Problem]:
    """
    获取Polygon中用户的题目列表
    
    Args:
        show_deleted: 是否显示已删除的题目（默认为False）
        problem_id: 按题目ID筛选
        name: 按题目名称筛选
        owner: 按题目所有者筛选
        
    Returns:
        List[Problem]: 题目列表
        
    Raises:
        ValueError: 当环境变量未设置时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    return get_polygon_problems(
        api_key=api_key,
        api_secret=api_secret,
        show_deleted=show_deleted,
        problem_id=problem_id,
        name=name,
        owner=owner
    )

@mcp.tool()
def get_problem_info(problem_id: int) -> ProblemInfo:
    """
    获取Polygon题目的基本信息
    
    Args:
        problem_id: 题目ID
        
    Returns:
        ProblemInfo: 题目的基本信息，包含以下字段：
            - inputFile: 题目的输入文件名
            - outputFile: 题目的输出文件名
            - interactive: 是否为交互题
            - timeLimit: 时间限制（毫秒）
            - memoryLimit: 内存限制（MB）
            
    Raises:
        ValueError: 当环境变量未设置时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    return get_polygon_problem_info(
        api_key=api_key,
        api_secret=api_secret,
        problem_id=problem_id
    )

@mcp.tool()
def get_problem_statements(problem_id: int, pin: Optional[str] = None) -> Dict[str, Statement]:
    """
    获取Polygon题目的多语言陈述
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        Dict[str, Statement]: 语言代码到题目陈述的映射，每个Statement包含：
            - encoding: 陈述的编码格式
            - name: 该语言下的题目名称
            - legend: 题目描述
            - input: 输入格式说明
            - output: 输出格式说明
            - scoring: 评分说明（可选）
            - interaction: 交互协议说明（仅用于交互题，可选）
            - notes: 题目注释（可选）
            - tutorial: 题解（可选）
            
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    statements = session.get_statements()
    return statements.items

@mcp.tool()
def get_problem_checker(problem_id: int, pin: Optional[str] = None) -> str:
    """
    获取Polygon题目当前使用的checker文件名
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: checker文件名
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.get_checker()

@mcp.tool()
def get_problem_validator(problem_id: int, pin: Optional[str] = None) -> str:
    """
    获取Polygon题目当前使用的validator文件名
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: validator文件名
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.get_validator()

@mcp.tool()
def get_problem_interactor(problem_id: int, pin: Optional[str] = None) -> str:
    """
    获取Polygon题目当前使用的interactor文件名
    
    Args:
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        str: interactor文件名。如果题目不是交互题，可能返回空字符串
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    api_key, api_secret = _get_api_credentials()
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.get_interactor()

@mcp.tool()
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
    api_key, api_secret = _get_api_credentials()
    
    # 验证文件类型
    try:
        file_type_enum = FileType(file_type)
    except ValueError:
        raise ValueError(
            f"无效的文件类型: {file_type}\n"
            "可选值: resource, source, aux"
        )
    
    client = PolygonClient(api_key, api_secret)
    session = client.create_problem_session(problem_id, pin)
    return session.view_file(file_type_enum, file_name)

if __name__ == "__main__":
    mcp.run()