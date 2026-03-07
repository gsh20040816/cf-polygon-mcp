import hashlib
import random
import time
from typing import Any, Dict, Mapping, Optional, Union

import requests

from src.polygon.models import (
    AccessDeniedException,
    PolygonBusinessError,
    PolygonHTTPError,
    PolygonNetworkError,
)

DEFAULT_RETRY_STATUS_CODES = frozenset({429, 502, 503, 504})
DEFAULT_MAX_RETRIES = 2
DEFAULT_RETRY_BACKOFF_SECONDS = 1.0
DEFAULT_MAX_BACKOFF_SECONDS = 8.0
DEFAULT_TIMEOUT_SECONDS = 30
MAX_RESPONSE_TEXT_LENGTH = 300


def generate_api_signature(api_secret: str, method_name: str, params: Mapping[str, Any]) -> str:
    """
    生成 Polygon API 签名。

    签名规则:
    1. 生成一个 6 位随机数作为 rand
    2. 将参数按 key 升序排序
    3. 拼接字符串: rand/method_name?param1=value1&param2=value2#api_secret
    4. 计算拼接字符串的 sha512hex
    5. 返回 rand + hex
    """
    rand = str(random.randint(100000, 999999))
    sorted_params = sorted(params.items(), key=lambda item: (item[0], str(item[1])))
    param_str = "&".join(f"{key}={value}" for key, value in sorted_params)

    signature_base = f"{rand}/{method_name}"
    if param_str:
        signature_base += f"?{param_str}"
    signature_base += f"#{api_secret}"

    sha = hashlib.sha512(signature_base.encode()).hexdigest()
    return f"{rand}{sha}"


def _prepare_request_params(
    api_key: str,
    api_secret: str,
    method: str,
    params: Optional[Mapping[str, Any]],
) -> dict[str, Any]:
    request_params = dict(params or {})
    request_params["apiKey"] = api_key
    request_params["time"] = str(int(time.time()))
    request_params["apiSig"] = generate_api_signature(api_secret, method, request_params)
    return request_params


def _truncate_response_text(response: Optional[requests.Response]) -> Optional[str]:
    if response is None:
        return None
    text = (response.text or "").strip()
    if not text:
        return None
    if len(text) <= MAX_RESPONSE_TEXT_LENGTH:
        return text
    return f"{text[:MAX_RESPONSE_TEXT_LENGTH]}..."


def _build_business_error(method: str, data: dict[str, Any]) -> PolygonBusinessError:
    comment = str(data.get("comment") or data.get("message") or "Unknown error")
    context_value = data.get("context")
    rendered_context = None if context_value in (None, "", [], {}) else str(context_value)
    message = f"Polygon 业务错误 ({method}): {comment}"
    if rendered_context is not None:
        message += f" [context={rendered_context}]"

    lowered_comment = comment.lower()
    if any(token in lowered_comment for token in ("access denied", "permission", "not allowed")):
        return AccessDeniedException(message, comment=comment, context=rendered_context)
    return PolygonBusinessError(message, comment=comment, context=rendered_context)


def _sleep_before_retry(
    attempt_index: int,
    *,
    response: Optional[requests.Response],
    retry_backoff_seconds: float,
    max_backoff_seconds: float,
) -> None:
    retry_after = response.headers.get("Retry-After") if response is not None else None
    if retry_after is not None:
        try:
            delay = float(retry_after)
        except ValueError:
            delay = None
    else:
        delay = None

    if delay is None:
        delay = min(max_backoff_seconds, retry_backoff_seconds * (2 ** attempt_index))
    time.sleep(delay)


def make_api_request(
    api_key: str,
    api_secret: str,
    base_url: str,
    method: str,
    params: Optional[Dict] = None,
    raw_response: bool = False,
    http_method: str = "GET",
    max_retries: Optional[int] = None,
    retry_backoff_seconds: Optional[float] = None,
    retry_status_codes: Optional[set[int]] = None,
    max_backoff_seconds: Optional[float] = None,
) -> Union[Dict, bytes]:
    """
    发送请求到 Polygon API。

    Args:
        api_key: API 密钥
        api_secret: API 密钥对应的秘钥
        base_url: API 基础 URL
        method: API 方法名
        params: 请求参数
        raw_response: 是否返回原始响应内容
        http_method: HTTP 方法
        max_retries: 可重试次数，不含首次请求
        retry_backoff_seconds: 指数退避的基础秒数
        retry_status_codes: 允许重试的 HTTP 状态码集合
        max_backoff_seconds: 单次最大退避等待秒数

    Returns:
        Union[Dict, bytes]: 如果 raw_response 为 True，返回原始响应内容；
        否则返回解析后的 JSON 数据
    """
    resolved_max_retries = DEFAULT_MAX_RETRIES if max_retries is None else max_retries
    if resolved_max_retries < 0:
        raise ValueError("max_retries 不能小于 0")

    resolved_retry_backoff = (
        DEFAULT_RETRY_BACKOFF_SECONDS
        if retry_backoff_seconds is None
        else retry_backoff_seconds
    )
    if resolved_retry_backoff <= 0:
        raise ValueError("retry_backoff_seconds 必须大于 0")

    resolved_max_backoff = (
        DEFAULT_MAX_BACKOFF_SECONDS if max_backoff_seconds is None else max_backoff_seconds
    )
    if resolved_max_backoff <= 0:
        raise ValueError("max_backoff_seconds 必须大于 0")

    resolved_retry_status_codes = (
        DEFAULT_RETRY_STATUS_CODES if retry_status_codes is None else set(retry_status_codes)
    )
    request_method = http_method.upper()

    for attempt_index in range(resolved_max_retries + 1):
        request_params = _prepare_request_params(api_key, api_secret, method, params)
        request_kwargs: dict[str, Any] = {"timeout": DEFAULT_TIMEOUT_SECONDS}
        if request_method == "GET":
            request_kwargs["params"] = request_params
        else:
            request_kwargs["data"] = request_params

        try:
            response = requests.request(request_method, f"{base_url}{method}", **request_kwargs)
            response.raise_for_status()

            if raw_response:
                return response.content

            try:
                data = response.json()
            except ValueError as exc:
                raise PolygonHTTPError(
                    f"Polygon 响应解析失败 ({method})",
                    status_code=response.status_code,
                    response_text=_truncate_response_text(response),
                ) from exc

            if data.get("status") != "OK":
                raise _build_business_error(method, data)

            return data
        except requests.HTTPError as exc:
            response = exc.response
            status_code = response.status_code if response is not None else None
            if (
                status_code in resolved_retry_status_codes
                and attempt_index < resolved_max_retries
            ):
                _sleep_before_retry(
                    attempt_index,
                    response=response,
                    retry_backoff_seconds=resolved_retry_backoff,
                    max_backoff_seconds=resolved_max_backoff,
                )
                continue

            response_text = _truncate_response_text(response)
            message = f"Polygon HTTP 错误 ({method})"
            if status_code is not None:
                message += f": status={status_code}"
            if response_text is not None:
                message += f", response={response_text}"

            if status_code == 403:
                raise AccessDeniedException(message, comment=response_text) from exc
            raise PolygonHTTPError(
                message,
                status_code=status_code,
                response_text=response_text,
            ) from exc
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt_index < resolved_max_retries:
                _sleep_before_retry(
                    attempt_index,
                    response=None,
                    retry_backoff_seconds=resolved_retry_backoff,
                    max_backoff_seconds=resolved_max_backoff,
                )
                continue
            raise PolygonNetworkError(f"Polygon 网络请求失败 ({method}): {exc}") from exc
        except requests.RequestException as exc:
            raise PolygonNetworkError(f"Polygon 请求失败 ({method}): {exc}") from exc

    raise PolygonNetworkError(f"Polygon 请求失败 ({method}): 已耗尽所有重试")
