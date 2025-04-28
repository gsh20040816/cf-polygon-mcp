from typing import List, Dict, Optional, Union
from .models import Problem, ProblemInfo
from .problem import ProblemSession
from .contest import ContestSession

class PolygonClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://polygon.codeforces.com/api/"
        
    def get_problems(self, 
                    show_deleted: Optional[bool] = None,
                    problem_id: Optional[int] = None,
                    name: Optional[str] = None,
                    owner: Optional[str] = None) -> List[Problem]:
        """
        获取用户可访问的题目列表
        
        Args:
            show_deleted: 是否显示已删除的题目（默认为False）
            problem_id: 按题目ID筛选
            name: 按题目名称筛选
            owner: 按题目所有者筛选
            
        Returns:
            List[Problem]: 题目列表
        """
        from .api.problems import get_problems
        return get_problems(
            self.api_key, 
            self.api_secret, 
            self.base_url, 
            show_deleted, 
            problem_id, 
            name, 
            owner
        )

        
    def create_problem_session(self, problem_id: int, pin: Optional[str] = None) -> ProblemSession:
        """
        创建一个题目会话，用于执行题目相关的操作
        
        Args:
            problem_id: 题目ID
            pin: 题目的PIN码（如果有）
            
        Returns:
            ProblemSession: 题目会话对象
        """
        return ProblemSession(self, problem_id, pin)
        
    def create_contest_session(self, contest_id: int, pin: Optional[str] = None) -> ContestSession:
        """
        创建一个比赛会话，用于执行比赛相关的操作
        
        Args:
            contest_id: 比赛ID
            pin: 比赛的PIN码（如果有）
            
        Returns:
            ContestSession: 比赛会话对象
            
        Example:
            >>> contest = client.create_contest_session(12345)
            >>> problems = contest.get_problems()
            >>> for problem in problems:
            >>>     print(f"Problem: {problem.name}")
        """
        return ContestSession(self, contest_id, pin)
