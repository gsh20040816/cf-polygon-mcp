from typing import Optional

from src.mcp.utils.common import get_account_credentials
from src.polygon.download import (
    download_contest_descriptor as _download_contest_descriptor,
    download_contest_statements_pdf as _download_contest_statements_pdf,
    download_problem_descriptor as _download_problem_descriptor,
    download_problem_package as _download_problem_package,
)


def download_problem_package_by_url(
    problem_url: str,
    pin: Optional[str] = None,
    revision: Optional[int] = None,
    package_type: Optional[str] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
) -> bytes:
    """
    使用 Polygon 账号密码下载题目包。

    Args:
        problem_url: 题目主页 URL，例如 https://polygon.codeforces.com/p/owner/problem
        pin: 题目的 PIN（如果有）
        revision: 指定 revision（可选）
        package_type: 包类型，可选 linux 或 windows
        login: Polygon 登录名；不传则读取 POLYGON_LOGIN
        password: Polygon 密码；不传则读取 POLYGON_PASSWORD
    """
    if package_type is not None and package_type not in {"linux", "windows"}:
        raise ValueError("package_type 仅支持 linux 或 windows")

    resolved_login, resolved_password = get_account_credentials(login, password)
    return _download_problem_package(
        problem_url=problem_url,
        login=resolved_login,
        password=resolved_password,
        pin=pin,
        revision=revision,
        package_type=package_type,
    )


def download_problem_descriptor(
    problem_url: str,
    pin: Optional[str] = None,
    revision: Optional[int] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
) -> bytes:
    """使用 Polygon 账号密码下载题目 descriptor（problem.xml）。"""
    resolved_login, resolved_password = get_account_credentials(login, password)
    return _download_problem_descriptor(
        problem_url=problem_url,
        login=resolved_login,
        password=resolved_password,
        pin=pin,
        revision=revision,
    )


def download_contest_descriptor(
    contest_url: str,
    pin: Optional[str] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
) -> bytes:
    """使用 Polygon 账号密码下载比赛 descriptor（contest.xml）。"""
    resolved_login, resolved_password = get_account_credentials(login, password)
    return _download_contest_descriptor(
        contest_url=contest_url,
        login=resolved_login,
        password=resolved_password,
        pin=pin,
    )


def download_contest_statements_pdf(
    contest_url: str,
    language: str = "english",
    pin: Optional[str] = None,
    login: Optional[str] = None,
    password: Optional[str] = None,
) -> bytes:
    """使用 Polygon 账号密码下载比赛陈述 PDF。"""
    resolved_login, resolved_password = get_account_credentials(login, password)
    return _download_contest_statements_pdf(
        contest_url=contest_url,
        login=resolved_login,
        password=resolved_password,
        language=language,
        pin=pin,
    )
