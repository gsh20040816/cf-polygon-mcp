from typing import Dict, Optional
from src.polygon.client import PolygonClient
from src.mcp.utils.common import get_api_credentials

def get_contest_problems(
    contest_id: int,
    pin: Optional[str] = None
) -> Dict:
    """
    获取Polygon比赛中的所有题目
    
    Args:
        contest_id: 比赛ID
        pin: 比赛的PIN码（如果有）
        
    Returns:
        Dict: 包含状态信息和题目列表的字典：
            {
                "status": str,  # 操作状态
                "message": str,  # 状态消息
                "problems": List[Problem]  # 题目列表
            }
            
    Raises:
        ValueError: 当环境变量未设置时抛出
        PolygonException: 当API请求失败或返回数据格式不正确时
    """
    try:
        api_key, api_secret = get_api_credentials()
        
        status_message = f"正在获取比赛 {contest_id} 的题目..."
        print(status_message)
        
        client = PolygonClient(api_key, api_secret)
        session = client.create_contest_session(contest_id, pin)
        problems = session.get_problems()
        
        if not problems:
            error_message = f"比赛 {contest_id} 中没有找到题目。这可能是因为：\n" \
                          "1. 比赛ID不正确\n" \
                          "2. 没有访问权限\n" \
                          "3. PIN码错误或缺失"
            print(error_message)
            return {
                "status": "error",
                "message": error_message,
                "problems": []
            }
            
        result_message = f"成功获取到 {len(problems)} 个题目"
        print(result_message)
        problems_info = [f"- {problem}" for problem in problems]
        print("\n".join(problems_info))
            
        return {
            "status": "success",
            "message": result_message,
            "problems": problems
        }
        
    except ValueError as e:
        error_message = f"API凭证错误: {str(e)}"
        print(error_message)
        return {
            "status": "error",
            "message": error_message,
            "problems": []
        }
    except Exception as e:
        error_message = f"获取比赛题目失败: {str(e)}"
        print(error_message)
        return {
            "status": "error",
            "message": error_message,
            "problems": []
        } 