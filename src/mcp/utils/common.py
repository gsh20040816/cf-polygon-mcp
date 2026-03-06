import os
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Type

from src.polygon.client import PolygonClient

def get_api_credentials() -> tuple[str, str]:
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


def get_account_credentials(
    login: Optional[str] = None,
    password: Optional[str] = None,
) -> tuple[str, str]:
    """获取 Polygon 账号密码，参数优先，其次读取环境变量。"""
    resolved_login = login or os.getenv("POLYGON_LOGIN")
    resolved_password = password or os.getenv("POLYGON_PASSWORD")

    if not resolved_login or not resolved_password:
        raise ValueError(
            "请提供 Polygon 账号密码，或设置环境变量 POLYGON_LOGIN 和 POLYGON_PASSWORD"
        )

    return resolved_login, resolved_password


def get_client() -> PolygonClient:
    """创建一个带环境变量凭证的 PolygonClient。"""
    api_key, api_secret = get_api_credentials()
    return PolygonClient(api_key, api_secret)


def get_problem_session(problem_id: int, pin: Optional[str] = None):
    """创建题目会话。"""
    return get_client().create_problem_session(problem_id, pin)


def serialize_problem(problem: Any) -> dict[str, Any]:
    """把题目对象压平成适合工具返回的结构。"""
    return {
        "id": problem.id,
        "owner": getattr(problem, "owner", None),
        "name": problem.name,
        "access_type": problem.accessType.value,
        "revision": getattr(problem, "revision", None),
        "latest_package": getattr(problem, "latestPackage", None),
        "modified": getattr(problem, "modified", None),
        "contest_letter": getattr(problem, "contestLetter", None),
    }


def serialize_problem_info(info: Any) -> dict[str, Any]:
    """把 ProblemInfo 压平成字典。"""
    return {
        "input_file": info.inputFile,
        "output_file": info.outputFile,
        "interactive": info.interactive,
        "time_limit": info.timeLimit,
        "memory_limit": info.memoryLimit,
    }


def serialize_statement(statement: Any) -> dict[str, Any]:
    """把 Statement 压平成字典。"""
    return {
        "encoding": statement.encoding,
        "name": statement.name,
        "legend": statement.legend,
        "input": statement.input,
        "output": statement.output,
        "scoring": getattr(statement, "scoring", None),
        "interaction": getattr(statement, "interaction", None),
        "notes": getattr(statement, "notes", None),
        "tutorial": getattr(statement, "tutorial", None),
    }


def is_ok_result(result: Any) -> bool:
    """判断底层返回是否表示成功。"""
    if not isinstance(result, dict):
        return True
    return result.get("status", "OK") in ("OK", "success")


def build_operation_result(
    *,
    action: str,
    success: bool,
    message: str,
    result: Any = None,
    error: Optional[Exception] = None,
    status_override: Optional[str] = None,
    **context: Any,
) -> dict[str, Any]:
    """构建统一的工具返回结构。"""
    payload: dict[str, Any] = {
        "status": status_override or ("success" if success else "error"),
        "action": action,
        "message": message,
    }
    if result is not None:
        payload["result"] = result
    if error is not None:
        payload["error"] = str(error)
        payload["error_type"] = type(error).__name__
    for key, value in context.items():
        if value is not None:
            payload[key] = value
    return payload


def parse_enum(enum_type: Type[Enum], value: str, field_name: str):
    """把字符串解析为枚举，出错时返回更友好的提示。"""
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed_values = ", ".join(item.value for item in enum_type)
        raise ValueError(f"无效的 {field_name}: {value}，可选值: {allowed_values}") from exc


def resolve_text_input(
    text: Optional[str],
    local_path: Optional[str],
    field_name: str,
) -> str:
    """在直接文本和本地文件之间解析输入内容。"""
    if (text is None) == (local_path is None):
        raise ValueError(f"{field_name} 和 local_path 必须且只能提供一个")

    if local_path is None:
        return text

    path = Path(local_path).expanduser()
    if not path.is_file():
        raise ValueError(f"local_path 不是有效文件: {local_path}")

    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"local_path 必须指向 UTF-8 文本文件: {local_path}") from exc


def resolve_upload_name(
    name: Optional[str],
    local_path: Optional[str],
    field_name: str,
) -> str:
    """优先使用显式名称，否则从本地文件路径推导文件名。"""
    if name is not None and name.strip():
        return name
    if local_path is not None:
        return Path(local_path).expanduser().name
    raise ValueError(f"{field_name} 不能为空")
