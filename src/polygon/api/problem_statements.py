from typing import Optional
from src.polygon.models import LanguageMap, Statement
from src.polygon.utils.problem_utils import make_problem_request

def get_problem_statements(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    pin: Optional[str] = None
) -> LanguageMap[Statement]:
    """
    获取题目的多语言陈述
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        pin: 题目的PIN码（如果有）
        
    Returns:
        LanguageMap[Statement]: 语言到题目陈述的映射
        
    Example:
        >>> statements = get_problem_statements(api_key, api_secret, base_url, 12345)
        >>> # 获取英文陈述
        >>> en_statement = statements.get("english")
        >>> if en_statement:
        >>>     print(f"Title: {en_statement.name}")
        >>>     print(f"Description: {en_statement.legend}")
        >>> # 获取所有可用语言
        >>> print(f"Available languages: {list(statements.keys())}")
    """
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.statements", problem_id, pin
    )
    return LanguageMap.from_dict(response["result"], Statement) 