from mcp.server.fastmcp import FastMCP
from src.tools.problems import get_polygon_problems, get_polygon_problem_info
from typing import List, Optional
from src.polygon.models import Problem, ProblemInfo
import os

# Create an MCP server
mcp = FastMCP("CF-Polygon-MCP")


# Add an addition tool
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
    api_key = os.getenv("POLYGON_API_KEY")
    api_secret = os.getenv("POLYGON_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "请设置环境变量 POLYGON_API_KEY 和 POLYGON_API_SECRET\n"
            "可以通过以下方式设置:\n"
            "export POLYGON_API_KEY=your_key\n"
            "export POLYGON_API_SECRET=your_secret"
        )
    
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
    api_key = os.getenv("POLYGON_API_KEY")
    api_secret = os.getenv("POLYGON_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "请设置环境变量 POLYGON_API_KEY 和 POLYGON_API_SECRET\n"
            "可以通过以下方式设置:\n"
            "export POLYGON_API_KEY=your_key\n"
            "export POLYGON_API_SECRET=your_secret"
        )
    
    return get_polygon_problem_info(
        api_key=api_key,
        api_secret=api_secret,
        problem_id=problem_id
    )


if __name__ == "__main__":
    mcp.run()