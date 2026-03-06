from typing import Optional

from src.mcp.utils.common import get_problem_session, parse_enum
from src.polygon.models import Package, PackageType


def get_problem_packages(
    problem_id: int,
    pin: Optional[str] = None,
) -> list[Package]:
    """获取题目的历史包列表。"""
    return get_problem_session(problem_id, pin).get_packages()


def download_problem_package(
    problem_id: int,
    package_id: int,
    pin: Optional[str] = None,
    package_type: Optional[str] = None,
) -> bytes:
    """下载题目包。"""
    package_type_enum = (
        parse_enum(PackageType, package_type, "package_type") if package_type is not None else None
    )
    return get_problem_session(problem_id, pin).download_package(
        package_id=package_id,
        package_type=package_type_enum,
    )


def build_problem_package(
    problem_id: int,
    full: bool,
    verify: bool,
    pin: Optional[str] = None,
):
    """触发一次题目打包。"""
    return get_problem_session(problem_id, pin).build_package(full=full, verify=verify)


def commit_problem_changes(
    problem_id: int,
    pin: Optional[str] = None,
    minor_changes: Optional[bool] = None,
    message: Optional[str] = None,
):
    """提交工作副本修改。"""
    return get_problem_session(problem_id, pin).commit_changes(
        minor_changes=minor_changes,
        message=message,
    )
