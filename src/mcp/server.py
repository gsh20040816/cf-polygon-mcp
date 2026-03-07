from importlib.metadata import PackageNotFoundError, version
from typing import TYPE_CHECKING, Any

from src.mcp.tool_registry import iter_tool_registrations, validate_tool_registry

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


_mcp_instance = None


def _get_server_version() -> str:
    for package_name in ("cf-polygon-mcp", "cf_polygon_mcp"):
        try:
            return version(package_name)
        except PackageNotFoundError:
            continue
    return "unknown"


def _get_fastmcp_class():
    from mcp.server.fastmcp import FastMCP

    return FastMCP


def register_tools(mcp_server: Any) -> list[str]:
    """按注册表顺序向 MCP 服务注册全部工具。"""
    validate_tool_registry()
    registered_names: list[str] = []
    for registration in iter_tool_registrations():
        mcp_server.tool()(registration.func)
        registered_names.append(registration.name)
    return registered_names


def create_mcp():
    fast_mcp_class = _get_fastmcp_class()
    mcp_server = fast_mcp_class("CF-Polygon-MCP")
    mcp_server._mcp_server.version = _get_server_version()
    register_tools(mcp_server)
    return mcp_server


def get_mcp():
    global _mcp_instance
    if _mcp_instance is None:
        _mcp_instance = create_mcp()
    return _mcp_instance
