from typing import Optional, Dict, Union, List
from .models import (
    ProblemInfo, AccessType, AccessDeniedException,
    Statement, LanguageMap, FileType, Solution
)

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
    
    def _make_problem_request(
        self,
        method: str,
        params: Optional[Dict] = None,
        raw_response: bool = False
    ) -> Union[Dict, bytes]:
        """
        发送题目相关的API请求
        
        Args:
            method: API方法名
            params: 请求参数
            raw_response: 是否返回原始响应内容
            
        Returns:
            Union[Dict, bytes]: API响应数据或原始内容
        """
        if params is None:
            params = {}
            
        # 添加题目ID和PIN码（如果有）
        params["problemId"] = str(self.problem_id)
        if self.pin is not None:
            params["pin"] = self.pin
            
        return self.client._make_request(method, params, raw_response)
    
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
        
    def get_checker(self) -> str:
        """
        获取当前设置的checker文件名
        
        Returns:
            str: checker文件名
            
        Example:
            >>> checker_name = problem.get_checker()
            >>> print(f"Current checker: {checker_name}")
        """
        response = self._make_problem_request("problem.checker")
        return response["result"]
        
    def get_validator(self) -> str:
        """
        获取当前设置的validator文件名
        
        Returns:
            str: validator文件名
            
        Example:
            >>> validator_name = problem.get_validator()
            >>> print(f"Current validator: {validator_name}")
        """
        response = self._make_problem_request("problem.validator")
        return response["result"]
        
    def get_interactor(self) -> str:
        """
        获取当前设置的interactor文件名
        
        Returns:
            str: interactor文件名。如果题目不是交互题，可能返回空字符串
            
        Example:
            >>> interactor_name = problem.get_interactor()
            >>> if interactor_name:
            >>>     print(f"Current interactor: {interactor_name}")
            >>> else:
            >>>     print("Not an interactive problem")
        """
        response = self._make_problem_request("problem.interactor")
        return response["result"]
        
    def view_file(self, file_type: FileType, name: str) -> bytes:
        """
        获取文件内容
        
        Args:
            file_type: 文件类型（resource/source/aux）
            name: 文件名
            
        Returns:
            bytes: 文件内容的原始数据
            
        Example:
            >>> # 查看checker源代码
            >>> content = problem.view_file(FileType.SOURCE, "checker.cpp")
            >>> print(content.decode('utf-8'))
            >>> 
            >>> # 查看资源文件
            >>> content = problem.view_file(FileType.RESOURCE, "testlib.h")
            >>> print(content.decode('utf-8'))
        """
        params = {
            "type": file_type.value,
            "name": name
        }
        return self._make_problem_request("problem.viewFile", params, raw_response=True)
        
    def get_solutions(self) -> List[Solution]:
        """
        获取题目的所有解决方案
        
        Returns:
            List[Solution]: 解决方案列表，每个解决方案包含：
                - name: 文件名
                - modificationTimeSeconds: 修改时间
                - length: 文件长度
                - tag: 解法标签（main/ok/wa/tl等）
                
        Example:
            >>> solutions = problem.get_solutions()
            >>> for solution in solutions:
            >>>     print(f"Solution: {solution.name}")
            >>>     print(f"Type: {solution.get_verdict()}")
            >>>     if solution.is_correct():
            >>>         print("This is a correct solution")
        """
        response = self._make_problem_request("problem.solutions")
        return [Solution.from_dict(sol) for sol in response["result"]]
        
    def view_solution(self, name: str) -> bytes:
        """
        获取解决方案源代码
        
        Args:
            name: 解决方案文件名
            
        Returns:
            bytes: 解决方案源代码的原始内容
            
        Example:
            >>> # 查看主要解法的源代码
            >>> content = problem.view_solution("main.cpp")
            >>> print(content.decode('utf-8'))
            >>> 
            >>> # 查看错误解法的源代码
            >>> content = problem.view_solution("wrong_answer.py")
            >>> print(content.decode('utf-8'))
        """
        params = {
            "name": name
        }
        return self._make_problem_request("problem.viewSolution", params, raw_response=True) 