from typing import Optional

from src.polygon.models import AccessType, SolutionTag, SourceType
from src.polygon.utils.problem_utils import check_write_access, make_problem_request


def _bool_to_api(value: bool) -> str:
    return "true" if value else "false"


def _unwrap_result(response):
    if isinstance(response, dict) and "result" in response:
        return response["result"]
    return response


def set_problem_validator(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    validator: str,
    pin: Optional[str] = None,
):
    check_write_access(access_type)
    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.setValidator",
        problem_id,
        pin,
        {"validator": validator},
    )
    return _unwrap_result(response)


def set_problem_checker(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    checker: str,
    pin: Optional[str] = None,
):
    check_write_access(access_type)
    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.setChecker",
        problem_id,
        pin,
        {"checker": checker},
    )
    return _unwrap_result(response)


def set_problem_interactor(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    interactor: str,
    pin: Optional[str] = None,
):
    check_write_access(access_type)
    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.setInteractor",
        problem_id,
        pin,
        {"interactor": interactor},
    )
    return _unwrap_result(response)


def save_problem_solution(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    name: str,
    file_content: str,
    pin: Optional[str] = None,
    source_type: Optional[SourceType] = None,
    tag: Optional[SolutionTag] = None,
    check_existing: Optional[bool] = None,
):
    check_write_access(access_type)

    params = {
        "name": name,
        "file": file_content,
    }
    if source_type is not None:
        params["sourceType"] = source_type.value
    if tag is not None:
        params["tag"] = tag.value
    if check_existing is not None:
        params["checkExisting"] = _bool_to_api(check_existing)

    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.saveSolution",
        problem_id,
        pin,
        params,
        http_method="POST",
    )
    return _unwrap_result(response)


def edit_problem_solution_extra_tags(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    access_type: AccessType,
    name: str,
    remove: bool,
    pin: Optional[str] = None,
    testset: Optional[str] = None,
    test_group: Optional[str] = None,
    tag: Optional[SolutionTag] = None,
):
    check_write_access(access_type)

    if (testset is None) == (test_group is None):
        raise ValueError("testset 和 test_group 必须且只能提供一个")
    if not remove and tag is None:
        raise ValueError("添加额外标签时必须提供 tag")

    params = {
        "name": name,
        "remove": _bool_to_api(remove),
    }
    if testset is not None:
        params["testset"] = testset
    if test_group is not None:
        params["testGroup"] = test_group
    if tag is not None:
        params["tag"] = tag.value

    response = make_problem_request(
        api_key,
        api_secret,
        base_url,
        "problem.editSolutionExtraTags",
        problem_id,
        pin,
        params,
    )
    return _unwrap_result(response)
