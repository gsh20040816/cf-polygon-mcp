from typing import Optional, Dict, Union, List
from .models import (
    ProblemInfo, AccessType, AccessDeniedException,
    Statement, LanguageMap, FileType, Solution
)
from .api.problem_info import get_problem_info
from .api.problem_update_info import update_problem_info
from .api.problem_statements import get_problem_statements
from .api.problem_checker import get_problem_checker
from .api.problem_validator import get_problem_validator
from .api.problem_interactor import get_problem_interactor
from .api.problem_view_file import view_problem_file
from .api.problem_solutions import get_problem_solutions
from .api.problem_view_solution import view_problem_solution
from .api.problem_update_working_copy import update_problem_working_copy
from .api.problem_discard_working_copy import discard_problem_working_copy
from .api.problem_save_statement import save_problem_statement

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
            
        from .utils.problem_utils import check_write_access
        check_write_access(self._access_type)
    
    def get_info(self) -> ProblemInfo:
        """
        获取题目信息
        
        Returns:
            ProblemInfo: 题目的基本信息
        """
        return get_problem_info(
            self.client.api_key, 
            self.client.api_secret, 
            self.client.base_url, 
            self.problem_id
        )
    
    def update_info(self, 
                   input_file: Optional[str] = None,
                   output_file: Optional[str] = None,
                   time_limit: Optional[int] = None,
                   memory_limit: Optional[int] = None,
                   interactive: Optional[bool] = None) -> dict:
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
        if self._access_type is None:
            # 获取题目信息以检查访问权限
            problem = self.client.get_problems(problem_id=self.problem_id)[0]
            self._access_type = problem.accessType
            
        return update_problem_info(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin,
            self._access_type,
            input_file,
            output_file,
            time_limit,
            memory_limit,
            interactive
        )
        
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
        return get_problem_statements(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin
        )
        
    def get_checker(self) -> str:
        """
        获取当前设置的checker文件名
        
        Returns:
            str: checker文件名
            
        Example:
            >>> checker_name = problem.get_checker()
            >>> print(f"Current checker: {checker_name}")
        """
        return get_problem_checker(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin
        )
        
    def get_validator(self) -> str:
        """
        获取当前设置的validator文件名
        
        Returns:
            str: validator文件名
            
        Example:
            >>> validator_name = problem.get_validator()
            >>> print(f"Current validator: {validator_name}")
        """
        return get_problem_validator(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin
        )
        
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
        return get_problem_interactor(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin
        )
        
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
        return view_problem_file(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            file_type,
            name,
            self.pin
        )
        
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
        return get_problem_solutions(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin
        )
        
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
        return view_problem_solution(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            name,
            self.pin
        )
        
    def update_working_copy(self) -> dict:
        """
        更新工作副本
        
        将该题目的最新提交版本作为工作副本，用于后续修改
        
        Returns:
            dict: API响应
            
        Example:
            >>> result = problem.update_working_copy()
            >>> if "ok" in result:
            >>>     print("工作副本已更新")
        """
        if self._access_type is None:
            # 获取题目信息以检查访问权限
            problem = self.client.get_problems(problem_id=self.problem_id)[0]
            self._access_type = problem.accessType
            
        return update_problem_working_copy(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin,
            self._access_type
        )
        
    def discard_working_copy(self) -> dict:
        """
        丢弃工作副本
        
        丢弃对该题目的所有未提交修改
        
        Returns:
            dict: API响应
            
        Example:
            >>> result = problem.discard_working_copy()
            >>> if "ok" in result:
            >>>     print("工作副本已丢弃")
        """
        if self._access_type is None:
            # 获取题目信息以检查访问权限
            problem = self.client.get_problems(problem_id=self.problem_id)[0]
            self._access_type = problem.accessType
            
        return discard_problem_working_copy(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            self.pin,
            self._access_type
        )
        
    def save_statement(self, 
                      lang: str, 
                      encoding: str = "utf-8",
                      name: Optional[str] = None,
                      legend: Optional[str] = None,
                      input: Optional[str] = None,
                      output: Optional[str] = None,
                      scoring: Optional[str] = None,
                      interaction: Optional[str] = None,
                      notes: Optional[str] = None,
                      tutorial: Optional[str] = None) -> dict:
        """
        更新或创建题目的陈述
        
        Args:
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
            
        Returns:
            dict: API响应
            
        Raises:
            AccessDeniedException: 当没有足够的访问权限时抛出
            
        Example:
            >>> # 添加或更新英文题目描述
            >>> result = problem.save_statement(
            >>>     lang="english",
            >>>     name="Binary Search",
            >>>     legend="Implement a binary search algorithm...",
            >>>     input="The first line contains an integer n...",
            >>>     output="For each query, output the index..."
            >>> )
            >>> # 添加或更新中文题目描述
            >>> result = problem.save_statement(
            >>>     lang="chinese",
            >>>     name="二分查找",
            >>>     legend="实现一个二分查找算法...",
            >>>     input="第一行包含一个整数n...",
            >>>     output="对于每个查询，输出索引..."
            >>> )
        """
        if self._access_type is None:
            # 获取题目信息以检查访问权限
            problem = self.client.get_problems(problem_id=self.problem_id)[0]
            self._access_type = problem.accessType
            
        response = save_problem_statement(
            self.client.api_key,
            self.client.api_secret,
            self.client.base_url,
            self.problem_id,
            lang,
            self._access_type,
            self.pin,
            encoding,
            name,
            legend,
            input,
            output,
            scoring,
            interaction,
            notes,
            tutorial
        )
        
        # 确保返回dict类型
        if not isinstance(response, dict):
            return {"result": response}
            
        return response 