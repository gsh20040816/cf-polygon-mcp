from typing import Optional
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def save_problem_statement(
    problem_id: int,
    lang: str = "english",
    encoding: str = "UTF-8",
    name: Optional[str] = None,
    legend: Optional[str] = None,
    input: Optional[str] = None,
    output: Optional[str] = None,
    scoring: Optional[str] = None,
    interaction: Optional[str] = None,
    notes: Optional[str] = None,
    tutorial: Optional[str] = None,
    pin: Optional[str] = None
) -> dict:
    """
    更新或创建Polygon题目的陈述
    
    Args:
        problem_id: 题目ID
        lang: 陈述的语言 (必需)
        encoding: 陈述的编码格式（默认utf-8）
        name: 题目的名称
        legend: 题目的描述
        input: 题目的输入格式说明
        output: 题目的输出格式说明
        scoring: 题目的评分说明
        interaction: 题目的交互协议说明（仅用于交互题）
        notes: 题目注释
        tutorial: 题目教程/题解
        pin: 题目的PIN码（如果有）
        
    Returns:
        dict: 包含状态信息的响应
        
    Raises:
        ValueError: 当环境变量未设置时抛出
        AccessDeniedException: 当没有足够的访问权限时抛出
    """
    try:
        api_key, api_secret = get_api_credentials()
        
        client = PolygonClient(api_key, api_secret)
        session = client.create_problem_session(problem_id, pin)
        
        # 不直接获取result，因为可能会引发异常
        print(f"MCP 工具传入参数: notes={notes}, lang={lang}")
        session.save_statement(
            lang=lang,
            encoding=encoding,
            name=name,
            legend=legend,
            input=input,
            output=output,
            scoring=scoring,
            interaction=interaction,
            notes=notes,
            tutorial=tutorial
        )
        
        return {
            "status": "success",
            "message": f"题目{lang}陈述更新成功",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"题目{lang}陈述更新失败: {str(e)}",
            "error": str(e)
        }
