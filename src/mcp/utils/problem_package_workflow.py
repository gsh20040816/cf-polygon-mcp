from __future__ import annotations

import time
from typing import Any, Optional

from src.mcp.utils.common import get_problem_session
from src.polygon.models import Package, PackageState


def _extract_package_id(build_result: Any) -> Optional[int]:
    if isinstance(build_result, Package):
        return build_result.id
    if isinstance(build_result, int):
        return build_result
    if isinstance(build_result, dict):
        for key in ("packageId", "id"):
            value = build_result.get(key)
            if value is not None:
                return int(value)
        nested_package = build_result.get("package")
        if nested_package is not None:
            return _extract_package_id(nested_package)
    return None


def _serialize_package(package: Package) -> dict[str, Any]:
    return {
        "id": package.id,
        "revision": package.revision,
        "creation_time": package.creationTimeSeconds.isoformat(),
        "state": package.state.value,
        "comment": package.comment,
        "type": package.type.value,
    }


def _pick_latest_package(packages: list[Package]) -> Optional[Package]:
    if not packages:
        return None
    return max(packages, key=lambda package: (package.creationTimeSeconds, package.id))


def build_problem_package_and_wait(
    problem_id: int,
    full: bool,
    verify: bool,
    pin: Optional[str] = None,
    timeout_seconds: int = 600,
    poll_interval_seconds: float = 5.0,
) -> dict[str, Any]:
    """
    触发题目打包并等待构建完成。

    Returns:
        dict: 包含构建请求结果、匹配到的 package 信息和最终状态。
    """
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds 必须大于 0")
    if poll_interval_seconds <= 0:
        raise ValueError("poll_interval_seconds 必须大于 0")

    session = get_problem_session(problem_id, pin)
    existing_package_ids = {package.id for package in session.get_packages()}
    build_result = session.build_package(full=full, verify=verify)
    target_package_id = _extract_package_id(build_result)
    start_time = time.monotonic()
    polls = 0
    matched_package: Optional[Package] = None

    while True:
        packages = session.get_packages()
        if target_package_id is not None:
            matched_package = next(
                (package for package in packages if package.id == target_package_id),
                None,
            )
        else:
            new_packages = [package for package in packages if package.id not in existing_package_ids]
            matched_package = _pick_latest_package(new_packages)

        elapsed_seconds = round(time.monotonic() - start_time, 2)

        if matched_package is not None:
            if matched_package.state == PackageState.READY:
                return {
                    "status": "success",
                    "message": "题目包已构建完成",
                    "build_result": build_result,
                    "package": _serialize_package(matched_package),
                    "polls": polls,
                    "elapsed_seconds": elapsed_seconds,
                }
            if matched_package.state == PackageState.FAILED:
                return {
                    "status": "error",
                    "message": "题目包构建失败",
                    "build_result": build_result,
                    "package": _serialize_package(matched_package),
                    "polls": polls,
                    "elapsed_seconds": elapsed_seconds,
                }

        if elapsed_seconds >= timeout_seconds:
            return {
                "status": "timeout",
                "message": "等待题目包构建超时",
                "build_result": build_result,
                "package": _serialize_package(matched_package) if matched_package is not None else None,
                "polls": polls,
                "elapsed_seconds": elapsed_seconds,
                "target_package_id": target_package_id,
            }

        polls += 1
        time.sleep(poll_interval_seconds)
