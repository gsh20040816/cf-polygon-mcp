from typing import Optional, Dict
from .models import ProblemInfo, AccessType, AccessDeniedException, Statement, LanguageMap

class ProblemSession:
    """处理特定题目的会话类"""
    
    def __init__(self, client, problem_id: int, pin: Optional[str] = None):
        """
        初始化题目会话
        
        Args:
            client: PolygonClient实例
            problem_id: 题目ID
            pin: 题目的PIN码（如果有）
        """
        self.client = client
        self.problem_id = problem_id
        self.pin = pin
        self._access_type: Optional[AccessType] = None
        
    def _check_write_access(self):
        """检查是否有写入权限"""
        if self._access_type is None:
            # 获取题目信息以检查访问权限
            problem = self.client.get_problems(problem_id=self.problem_id)[0]
            self._access_type = problem.accessType
            
        if self._access_type == AccessType.READ:
            raise AccessDeniedException("需要WRITE或OWNER权限才能执行此操作")
    
    def _make_problem_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """
        发送题目相关的API请求
        
        Args:
            method: API方法名
            params: 请求参数
            
        Returns:
            Dict: API响应数据
        """
        if params is None:
            params = {}
            
        # 添加题目ID和PIN码（如果有）
        params["problemId"] = str(self.problem_id)
        if self.pin is not None:
            params["pin"] = self.pin
            
        return self.client._make_request(method, params)
    
    def get_info(self) -> ProblemInfo:
        """
        获取题目信息
        
        Returns:
            ProblemInfo: 题目的基本信息
        """
        response = self._make_problem_request("problem.info")
        return ProblemInfo.from_dict(response["result"])
    
    def update_info(self, 
                   input_file: Optional[str] = None,
                   output_file: Optional[str] = None,
                   time_limit: Optional[int] = None,
                   memory_limit: Optional[int] = None,
                   interactive: Optional[bool] = None) -> ProblemInfo:
        """
        更新题目信息
        
        Args:
            input_file: 输入文件名
            output_file: 输出文件名
            time_limit: 时间限制（毫秒）
            memory_limit: 内存限制（MB）
            interactive: 是否为交互题
            
        Returns:
            ProblemInfo: 更新后的题目信息
        """
        self._check_write_access()
        
        params = {}
        if input_file is not None:
            params["inputFile"] = input_file
        if output_file is not None:
            params["outputFile"] = output_file
        if time_limit is not None:
            params["timeLimit"] = str(time_limit)
        if memory_limit is not None:
            params["memoryLimit"] = str(memory_limit)
        if interactive is not None:
            params["interactive"] = "true" if interactive else "false"
            
        response = self._make_problem_request("problem.updateInfo", params)
        return ProblemInfo.from_dict(response["result"])
        
    def get_statements(self) -> LanguageMap[Statement]:
        """
        获取题目的多语言陈述
        
        Returns:
            LanguageMap[Statement]: 语言到题目陈述的映射
            
        Example:
            >>> statements = problem.get_statements()
            >>> # 获取英文陈述
            >>> en_statement = statements.get("english")
            >>> if en_statement:
            >>>     print(f"Title: {en_statement.name}")
            >>>     print(f"Description: {en_statement.legend}")
            >>> # 获取所有可用语言
            >>> print(f"Available languages: {list(statements.keys())}")
        """
        response = self._make_problem_request("problem.statements")
        return LanguageMap.from_dict(response["result"], Statement) 