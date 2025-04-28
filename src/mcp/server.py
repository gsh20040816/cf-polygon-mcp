from mcp.server.fastmcp import FastMCP
from src.mcp.utils.problems import get_problems
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_statements import get_problem_statements
from src.mcp.utils.problem_checker import get_problem_checker
from src.mcp.utils.problem_validator import get_problem_validator
from src.mcp.utils.problem_interactor import get_problem_interactor
from src.mcp.utils.problem_file import view_problem_file
from src.mcp.utils.problem_solutions import get_problem_solutions
from src.mcp.utils.problem_solution_view import view_problem_solution
from src.mcp.utils.contest_problems import get_contest_problems
from src.mcp.utils.problem_update_info import update_problem_info
from src.mcp.utils.problem_working_copy import update_problem_working_copy, discard_problem_working_copy
from src.mcp.utils.problem_save_statement import save_problem_statement

# 创建MCP服务器
mcp = FastMCP("CF-Polygon-MCP")

# 注册各个工具函数
mcp.tool()(get_problems)
mcp.tool()(get_problem_info)
mcp.tool()(get_problem_statements)
mcp.tool()(get_problem_checker)
mcp.tool()(get_problem_validator)
mcp.tool()(get_problem_interactor)
mcp.tool()(view_problem_file)
mcp.tool()(get_problem_solutions)
mcp.tool()(view_problem_solution)
mcp.tool()(get_contest_problems)
mcp.tool()(update_problem_info)
mcp.tool()(update_problem_working_copy)
mcp.tool()(discard_problem_working_copy)
mcp.tool()(save_problem_statement)
# 提供对外导出的接口
def get_mcp():
    return mcp 