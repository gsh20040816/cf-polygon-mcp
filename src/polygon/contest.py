from typing import Optional, Dict, List
from .models import Problem, AccessDeniedException, PolygonException
from .api.contest_problems import get_contest_problems

class ContestSession:
    """处理特定比赛的会话类"""
    
    def __init__(self, client, contest_id: int, pin: Optional[str] = None):
        """
        初始化比赛会话
        
        Args:
            client: PolygonClient实例
            contest_id: 比赛ID
            pin: 比赛的PIN码（如果有）
        """
        self.client = client
        self.contest_id = contest_id
        self.pin = pin
        
    def get_problems(self) -> List[Problem]:
        """
        获取比赛中的所有题目
        
        Returns:
            List[Problem]: 题目列表，每个题目包含：
                - id: 题目ID
                - name: 题目名称
                - owner: 题目所有者
                - accessType: 访问权限类型
                等字段
                
        Example:
            >>> problems = contest.get_problems()
            >>> for problem in problems:
            >>>     print(f"Problem: {problem.name}")
            >>>     print(f"Owner: {problem.owner}")
            >>>     print(f"Access: {problem.accessType}")
            
        Raises:
            PolygonException: 当API请求失败或返回数据格式不正确时
        """
        return get_contest_problems(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.contest_id,
            self.pin
        )
            
    def __str__(self) -> str:
        """返回比赛会话的字符串表示"""
        return f"ContestSession(id={self.contest_id})"
        
    def __repr__(self) -> str:
        """返回比赛会话的详细字符串表示"""
        return f"ContestSession(contest_id={self.contest_id}, pin={'***' if self.pin else 'None'})" 