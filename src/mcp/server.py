from src.mcp.utils.downloads import (
    download_contest_descriptor,
    download_contest_statements_pdf,
    download_problem_descriptor,
    download_problem_package_by_url,
)
from mcp.server.fastmcp import FastMCP
from src.mcp.utils.problem_content import (
    get_problem_files,
    get_problem_statement_resources,
    get_problem_tags,
    save_problem_file,
    save_problem_general_description,
    save_problem_general_tutorial,
    save_problem_script,
    save_problem_statement_resource,
    save_problem_tags,
    view_problem_general_description,
    view_problem_general_tutorial,
    view_problem_script,
)
from src.mcp.utils.problem_create import create_problem
from src.mcp.utils.problems import get_problems
from src.mcp.utils.problem_info import get_problem_info
from src.mcp.utils.problem_statements import get_problem_statements
from src.mcp.utils.problem_checker import get_problem_checker
from src.mcp.utils.problem_validator import get_problem_validator
from src.mcp.utils.problem_interactor import get_problem_interactor
from src.mcp.utils.problem_file import view_problem_file
from src.mcp.utils.problem_packages import (
    build_problem_package,
    commit_problem_changes,
    download_problem_package,
    get_problem_packages,
)
from src.mcp.utils.problem_solutions import get_problem_solutions
from src.mcp.utils.problem_solution_view import view_problem_solution
from src.mcp.utils.problem_sources import (
    edit_problem_solution_extra_tags,
    save_problem_solution,
    set_problem_checker,
    set_problem_interactor,
    set_problem_validator,
)
from src.mcp.utils.problem_tests_extended import (
    enable_problem_groups,
    enable_problem_points,
    get_problem_checker_tests,
    get_problem_tests,
    get_problem_validator_tests,
    save_problem_checker_test,
    save_problem_test,
    save_problem_test_group,
    save_problem_validator_test,
    set_problem_test_group,
    view_problem_test_answer,
    view_problem_test_groups,
    view_problem_test_input,
)
from src.mcp.utils.contest_problems import get_contest_problems
from src.mcp.utils.problem_update_info import update_problem_info
from src.mcp.utils.problem_working_copy import update_problem_working_copy, discard_problem_working_copy
from src.mcp.utils.problem_save_statement import save_problem_statement

# 创建MCP服务器
mcp = FastMCP("CF-Polygon-MCP")

# 注册各个工具函数
mcp.tool()(download_problem_package_by_url)
mcp.tool()(download_problem_descriptor)
mcp.tool()(download_contest_descriptor)
mcp.tool()(download_contest_statements_pdf)
mcp.tool()(create_problem)
mcp.tool()(get_problems)
mcp.tool()(get_problem_info)
mcp.tool()(get_problem_statements)
mcp.tool()(get_problem_statement_resources)
mcp.tool()(save_problem_statement_resource)
mcp.tool()(get_problem_checker)
mcp.tool()(set_problem_checker)
mcp.tool()(get_problem_validator)
mcp.tool()(set_problem_validator)
mcp.tool()(get_problem_interactor)
mcp.tool()(set_problem_interactor)
mcp.tool()(get_problem_files)
mcp.tool()(view_problem_file)
mcp.tool()(save_problem_file)
mcp.tool()(view_problem_script)
mcp.tool()(save_problem_script)
mcp.tool()(get_problem_tests)
mcp.tool()(view_problem_test_input)
mcp.tool()(view_problem_test_answer)
mcp.tool()(save_problem_test)
mcp.tool()(get_problem_validator_tests)
mcp.tool()(save_problem_validator_test)
mcp.tool()(get_problem_checker_tests)
mcp.tool()(save_problem_checker_test)
mcp.tool()(view_problem_test_groups)
mcp.tool()(save_problem_test_group)
mcp.tool()(set_problem_test_group)
mcp.tool()(enable_problem_groups)
mcp.tool()(enable_problem_points)
mcp.tool()(get_problem_solutions)
mcp.tool()(view_problem_solution)
mcp.tool()(save_problem_solution)
mcp.tool()(edit_problem_solution_extra_tags)
mcp.tool()(get_problem_tags)
mcp.tool()(save_problem_tags)
mcp.tool()(view_problem_general_description)
mcp.tool()(save_problem_general_description)
mcp.tool()(view_problem_general_tutorial)
mcp.tool()(save_problem_general_tutorial)
mcp.tool()(get_problem_packages)
mcp.tool()(download_problem_package)
mcp.tool()(build_problem_package)
mcp.tool()(get_contest_problems)
mcp.tool()(update_problem_info)
mcp.tool()(update_problem_working_copy)
mcp.tool()(commit_problem_changes)
mcp.tool()(discard_problem_working_copy)
mcp.tool()(save_problem_statement)
# 提供对外导出的接口
def get_mcp():
    return mcp 
