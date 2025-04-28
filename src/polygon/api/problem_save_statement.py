from typing import Optional
from src.polygon.models import AccessType, Statement
from src.polygon.utils.problem_utils import make_problem_request, check_write_access

def save_problem_statement(
    api_key: str,
    api_secret: str,
    base_url: str,
    problem_id: int,
    lang: str,
    access_type: AccessType,
    pin: Optional[str] = None,
    encoding: str = "UTF-8",
    name: Optional[str] = None,
    legend: Optional[str] = None,
    input: Optional[str] = None,
    output: Optional[str] = None,
    scoring: Optional[str] = None,
    interaction: Optional[str] = None,
    notes: Optional[str] = None,
    tutorial: Optional[str] = None
) -> dict:
    """
    更新或创建题目的陈述
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        problem_id: 题目ID
        lang: 陈述的语言 (必需)
        access_type: 用户的访问权限类型
        pin: 题目的PIN码（如果有）
        encoding: 陈述的编码格式（默认utf-8）
        name: 题目的名称
        legend: 题目的描述
        input: 题目的输入格式说明
        output: 题目的输出格式说明
        scoring: 题目的评分说明
        interaction: 题目的交互协议说明（仅用于交互题）
        notes: 题目注释
        tutorial: 题目教程/题解
        
    Returns:
        dict: API响应数据
        
    Raises:
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    # 检查是否有写入权限
    check_write_access(access_type)
    
    # 构建请求参数
    params = {
        "lang": lang,
        "encoding": encoding,
    }
    
    # 添加可选参数
    if name is not None:
        params["name"] = name
    if legend is not None:
        params["legend"] = legend
    if input is not None:
        params["input"] = input
    if output is not None:
        params["output"] = output
    if scoring is not None:
        params["scoring"] = scoring
    if interaction is not None:
        params["interaction"] = interaction
    if notes is not None:
        params["notes"] = notes
    if tutorial is not None:
        params["tutorial"] = tutorial
    
    # 打印请求参数，用于调试
    print("保存题目陈述请求参数:", params)
    
    # 发送请求
    response = make_problem_request(
        api_key, api_secret, base_url,
        "problem.saveStatement", problem_id, pin,
        params
    )
    
    if isinstance(response, dict) and "result" in response:
        return response["result"]
    return {"status": "OK"} 