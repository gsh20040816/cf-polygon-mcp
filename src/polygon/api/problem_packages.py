from typing import Optional

from src.polygon.models import AccessType, Package, PackageType
from src.polygon.utils.problem_utils import check_write_access, make_problem_request


def _bool_to_api(value: bool) -> str:
    return "true" if value else "false"


def _unwrap_result(response):
    if isinstance(response, dict) and "result" in response:
        return response["result"]
    return response


def get_problem_packages(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None,
) -> list[Package]:
    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.packages",
        problem_id,
        pin,
    )
    return [Package.from_dict(item) for item in response["result"]]


def download_problem_package(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    package_id: int,
    pin: Optional[str] = None,
    package_type: Optional[PackageType] = None,
) -> bytes:
    params = {"packageId": str(package_id)}
    if package_type is not None:
        params["type"] = package_type.value

    return make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.package",
        problem_id,
        pin,
        params,
        raw_response=True,
    )


def build_problem_package(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    full: bool,
    verify: bool,
    pin: Optional[str] = None,
):
    check_write_access(access_type)

    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.buildPackage",
        problem_id,
        pin,
        {
            "full": _bool_to_api(full),
            "verify": _bool_to_api(verify),
        },
    )
    return _unwrap_result(response)


def commit_problem_changes(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    pin: Optional[str] = None,
    minor_changes: Optional[bool] = None,
    message: Optional[str] = None,
):
    check_write_access(access_type)

    params = {}
    if minor_changes is not None:
        params["minorChanges"] = _bool_to_api(minor_changes)
    if message is not None:
        params["message"] = message

    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.commitChanges",
        problem_id,
        pin,
        params,
    )
    return _unwrap_result(response)
