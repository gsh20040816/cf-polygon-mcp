from typing import List, Optional

from src.polygon.models import PolygonException, Problem
from src.polygon.utils.contest_utils import make_contest_request


def _is_letter_mapping(data: dict) -> bool:
    return bool(data) and all(isinstance(key, str) and len(key) == 1 and key.isupper() for key in data)


def _extract_problem_records(payload) -> list[tuple[Optional[str], dict]]:
    if isinstance(payload, list):
        return [(None, item) for item in payload if isinstance(item, dict)]

    if not isinstance(payload, dict):
        raise PolygonException(
            f"Invalid result format: expected dict or list, got {type(payload)}"
        )

    if _is_letter_mapping(payload):
        return [
            (letter, item)
            for letter, item in payload.items()
            if isinstance(item, dict)
        ]

    for field in ("problems", "problemsList", "items", "list"):
        value = payload.get(field)
        if isinstance(value, list):
            return [(None, item) for item in value if isinstance(item, dict)]

    nested_result = payload.get("result")
    if isinstance(nested_result, (dict, list)):
        return _extract_problem_records(nested_result)

    values = list(payload.values())
    if values and all(isinstance(item, dict) for item in values):
        return [(None, item) for item in values]

    raise PolygonException("Invalid problems data format: unable to extract problem records")


def get_contest_problems(
    api_key: str,
    api_secret: str,
    base_url: str,
    contest_id: int,
    pin: Optional[str] = None,
) -> List[Problem]:
    """
    获取比赛中的所有题目。

    Raises:
        PolygonException: 当 API 请求失败或返回数据格式不正确时抛出。
    """
    try:
        response = make_contest_request(
            api_key,
            api_secret,
            base_url,
            "contest.problems",
            contest_id,
            pin,
        )

        if not isinstance(response, dict):
            raise PolygonException(
                f"Invalid response format: expected dict, got {type(response)}"
            )

        payload = response.get("result", response)
        records = _extract_problem_records(payload)

        problems: list[Problem] = []
        for contest_letter, problem_data in records:
            try:
                parsed = dict(problem_data)
                if contest_letter is not None:
                    parsed["contestLetter"] = contest_letter
                problems.append(Problem.from_dict(parsed))
            except Exception:
                continue

        problems.sort(key=lambda problem: getattr(problem, "contestLetter", "Z"))
        return problems
    except PolygonException:
        raise
    except Exception as exc:
        raise PolygonException(f"Failed to get contest problems: {exc}") from exc
