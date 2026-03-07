from src.mcp.utils.common import build_operation_result, get_client, serialize_problem


def create_problem(name: str) -> dict:
    """
    创建一个新的空 Polygon 题目。

    Args:
        name: 题目名称

    Returns:
        dict: 结构化创建结果
    """
    try:
        problem = get_client().create_problem(name)
    except Exception as exc:
        return build_operation_result(
            action="create_problem",
            success=False,
            message="题目创建失败",
            error=exc,
            name=name,
        )

    serialized_problem = serialize_problem(problem)
    return build_operation_result(
        action="create_problem",
        success=True,
        message="题目已创建",
        result=serialized_problem,
        name=name,
        problem=serialized_problem,
    )
