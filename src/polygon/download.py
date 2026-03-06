from typing import Optional

import requests


def _post_download(url: str, login: str, password: str, **extra_params) -> bytes:
    params = {
        "login": login,
        "password": password,
    }
    params.update({key: value for key, value in extra_params.items() if value is not None})

    response = requests.post(url, data=params, timeout=30)
    response.raise_for_status()
    return response.content


def _with_suffix(url: str, suffix: str) -> str:
    normalized = url.rstrip("/")
    if normalized.endswith(suffix):
        return normalized
    return f"{normalized}/{suffix}"


def download_problem_package(
    problem_url: str,
    login: str,
    password: str,
    pin: Optional[str] = None,
    revision: Optional[int] = None,
    package_type: Optional[str] = None,
) -> bytes:
    """下载题目包。"""
    return _post_download(
        problem_url.rstrip("/"),
        login,
        password,
        pin=pin,
        revision=str(revision) if revision is not None else None,
        type=package_type,
    )


def download_problem_descriptor(
    problem_url: str,
    login: str,
    password: str,
    pin: Optional[str] = None,
    revision: Optional[int] = None,
) -> bytes:
    """下载 problem.xml。"""
    return _post_download(
        _with_suffix(problem_url, "problem.xml"),
        login,
        password,
        pin=pin,
        revision=str(revision) if revision is not None else None,
    )


def download_contest_descriptor(
    contest_url: str,
    login: str,
    password: str,
    pin: Optional[str] = None,
) -> bytes:
    """下载 contest.xml。"""
    return _post_download(
        _with_suffix(contest_url, "contest.xml"),
        login,
        password,
        pin=pin,
    )


def download_contest_statements_pdf(
    contest_url: str,
    login: str,
    password: str,
    language: str = "english",
    pin: Optional[str] = None,
) -> bytes:
    """下载比赛陈述 PDF。"""
    return _post_download(
        _with_suffix(contest_url, f"{language}/statements.pdf"),
        login,
        password,
        pin=pin,
    )
