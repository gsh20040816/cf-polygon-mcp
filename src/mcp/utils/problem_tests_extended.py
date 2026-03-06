from typing import Optional

from src.mcp.utils.common import get_problem_session, parse_enum
from src.polygon.models import (
    CheckerTest,
    CheckerTestVerdict,
    FeedbackPolicy,
    PointsPolicy,
    Test,
    TestGroup,
    ValidatorTest,
    ValidatorTestVerdict,
)


def get_problem_tests(
    problem_id: int,
    testset: str,
    pin: Optional[str] = None,
    no_inputs: Optional[bool] = None,
) -> list[Test]:
    """获取题目测试列表。"""
    return get_problem_session(problem_id, pin).get_tests(testset=testset, no_inputs=no_inputs)


def view_problem_test_input(
    problem_id: int,
    testset: str,
    test_index: int,
    pin: Optional[str] = None,
) -> bytes:
    """查看某个测试输入。"""
    return get_problem_session(problem_id, pin).view_test_input(testset, test_index)


def view_problem_test_answer(
    problem_id: int,
    testset: str,
    test_index: int,
    pin: Optional[str] = None,
) -> bytes:
    """查看某个测试答案。"""
    return get_problem_session(problem_id, pin).view_test_answer(testset, test_index)


def save_problem_test(
    problem_id: int,
    testset: str,
    test_index: int,
    pin: Optional[str] = None,
    test_input: Optional[str] = None,
    test_group: Optional[str] = None,
    test_points: Optional[float] = None,
    test_description: Optional[str] = None,
    test_use_in_statements: Optional[bool] = None,
    test_input_for_statements: Optional[str] = None,
    test_output_for_statements: Optional[str] = None,
    verify_input_output_for_statements: Optional[bool] = None,
    check_existing: Optional[bool] = None,
):
    """保存一个测试。"""
    return get_problem_session(problem_id, pin).save_test(
        testset=testset,
        test_index=test_index,
        test_input=test_input,
        test_group=test_group,
        test_points=test_points,
        test_description=test_description,
        test_use_in_statements=test_use_in_statements,
        test_input_for_statements=test_input_for_statements,
        test_output_for_statements=test_output_for_statements,
        verify_input_output_for_statements=verify_input_output_for_statements,
        check_existing=check_existing,
    )


def get_problem_validator_tests(
    problem_id: int,
    pin: Optional[str] = None,
) -> list[ValidatorTest]:
    """获取 validator 测试列表。"""
    return get_problem_session(problem_id, pin).get_validator_tests()


def save_problem_validator_test(
    problem_id: int,
    test_index: int,
    pin: Optional[str] = None,
    test_verdict: Optional[str] = None,
    test_input: Optional[str] = None,
    test_group: Optional[str] = None,
    testset: Optional[str] = None,
    check_existing: Optional[bool] = None,
):
    """保存一个 validator 测试。"""
    verdict_enum = (
        parse_enum(ValidatorTestVerdict, test_verdict, "test_verdict")
        if test_verdict is not None
        else None
    )
    return get_problem_session(problem_id, pin).save_validator_test(
        test_index=test_index,
        test_verdict=verdict_enum,
        test_input=test_input,
        test_group=test_group,
        testset=testset,
        check_existing=check_existing,
    )


def get_problem_checker_tests(
    problem_id: int,
    pin: Optional[str] = None,
) -> list[CheckerTest]:
    """获取 checker 测试列表。"""
    return get_problem_session(problem_id, pin).get_checker_tests()


def save_problem_checker_test(
    problem_id: int,
    test_index: int,
    pin: Optional[str] = None,
    test_verdict: Optional[str] = None,
    test_input: Optional[str] = None,
    test_output: Optional[str] = None,
    test_answer: Optional[str] = None,
    check_existing: Optional[bool] = None,
):
    """保存一个 checker 测试。"""
    verdict_enum = (
        parse_enum(CheckerTestVerdict, test_verdict, "test_verdict")
        if test_verdict is not None
        else None
    )
    return get_problem_session(problem_id, pin).save_checker_test(
        test_index=test_index,
        test_verdict=verdict_enum,
        test_input=test_input,
        test_output=test_output,
        test_answer=test_answer,
        check_existing=check_existing,
    )


def view_problem_test_groups(
    problem_id: int,
    testset: str,
    pin: Optional[str] = None,
    group: Optional[str] = None,
) -> list[TestGroup]:
    """查看测试组配置。"""
    return get_problem_session(problem_id, pin).view_test_groups(testset=testset, group=group)


def save_problem_test_group(
    problem_id: int,
    testset: str,
    group: str,
    pin: Optional[str] = None,
    points_policy: Optional[str] = None,
    feedback_policy: Optional[str] = None,
    dependencies: Optional[list[str]] = None,
):
    """保存测试组配置。"""
    points_policy_enum = (
        parse_enum(PointsPolicy, points_policy, "points_policy")
        if points_policy is not None
        else None
    )
    feedback_policy_enum = (
        parse_enum(FeedbackPolicy, feedback_policy, "feedback_policy")
        if feedback_policy is not None
        else None
    )
    return get_problem_session(problem_id, pin).save_test_group(
        testset=testset,
        group=group,
        points_policy=points_policy_enum,
        feedback_policy=feedback_policy_enum,
        dependencies=dependencies,
    )


def set_problem_test_group(
    problem_id: int,
    testset: str,
    test_group: str,
    pin: Optional[str] = None,
    test_index: Optional[int] = None,
    test_indices: Optional[list[int]] = None,
):
    """把测试分配到某个测试组。"""
    return get_problem_session(problem_id, pin).set_test_group(
        testset=testset,
        test_group=test_group,
        test_index=test_index,
        test_indices=test_indices,
    )


def enable_problem_groups(
    problem_id: int,
    testset: str,
    enable: bool,
    pin: Optional[str] = None,
):
    """启用或关闭测试组。"""
    return get_problem_session(problem_id, pin).enable_groups(testset=testset, enable=enable)


def enable_problem_points(
    problem_id: int,
    enable: bool,
    pin: Optional[str] = None,
):
    """启用或关闭点数模式。"""
    return get_problem_session(problem_id, pin).enable_points(enable=enable)
