import os
from enum import Enum
from typing import Optional, Type

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


def get_client() -> PolygonClient:
    """创建一个带环境变量凭证的 PolygonClient。"""
    api_key, api_secret = get_api_credentials()
    return PolygonClient(api_key, api_secret)


def get_problem_session(problem_id: int, pin: Optional[str] = None):
    """创建题目会话。"""
    return get_client().create_problem_session(problem_id, pin)


def parse_enum(enum_type: Type[Enum], value: str, field_name: str):
    """把字符串解析为枚举，出错时返回更友好的提示。"""
    try:
        return enum_type(value)
    except ValueError as exc:
        allowed_values = ", ".join(item.value for item in enum_type)
        raise ValueError(f"无效的 {field_name}: {value}，可选值: {allowed_values}") from exc
