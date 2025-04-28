from typing import Optional, Dict, List
from .models import Problem, AccessDeniedException, PolygonException

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
        
    def _make_contest_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """
        发送比赛相关的API请求
        
        Args:
            method: API方法名
            params: 请求参数
            
        Returns:
            Dict: API响应数据
            
        Raises:
            PolygonException: 当API请求失败时
        """
        if params is None:
            params = {}
            
        # 添加比赛ID和PIN码（如果有）
        params["contestId"] = str(self.contest_id)
        if self.pin is not None:
            params["pin"] = self.pin
            
        return self.client._make_request(method, params)
    
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
        try:
            print("Requesting contest data...")
            response = self._make_contest_request("contest.problems")
            
            # 添加调试输出，查看API返回的实际数据结构
            print(f"API response: {response}")
            
            # 检查响应格式
            if not isinstance(response, dict):
                raise PolygonException(
                    f"Invalid response format: expected dict, got {type(response)}"
                )
                
            result = response.get("result")
            if result is None:
                # 尝试直接使用response作为结果
                print("Warning: Missing 'result' field in API response, trying to use response directly")
                result = response
                
            print(f"Result structure: {result}")
            
            # 如果result是字典，检查是否使用字母作为键（A, B, C...）
            if isinstance(result, dict):
                # 检查是否所有的键都是单个大写字母
                if all(len(key) == 1 and key.isupper() for key in result.keys()):
                    print("Found letter-based problem format")
                    problems_data = list(result.values())
                else:
                    # 尝试其他可能的格式
                    if "problems" in result:
                        problems_data = result["problems"]
                    elif "result" in result and isinstance(result["result"], (list, dict)):
                        # 有些API可能返回嵌套的result字段
                        nested_result = result["result"]
                        if isinstance(nested_result, list):
                            problems_data = nested_result
                        elif isinstance(nested_result, dict) and "problems" in nested_result:
                            problems_data = nested_result["problems"]
                        else:
                            possible_fields = ["problems", "problemsList", "items", "list"]
                            for field in possible_fields:
                                if field in nested_result and isinstance(nested_result[field], list):
                                    problems_data = nested_result[field]
                                    break
                            else:
                                # 如果是字典但找不到已知字段，尝试直接使用值列表
                                problems_data = list(nested_result.values())
                    else:
                        possible_fields = ["problems", "problemsList", "items", "list"]
                        for field in possible_fields:
                            if field in result and isinstance(result[field], list):
                                problems_data = result[field]
                                break
                        else:
                            # 打印可用字段，以便调试
                            field_list = ', '.join(sorted(result.keys()))
                            print(f"Available fields in result: {field_list}")
                            # 如果找不到已知字段，尝试直接使用值列表
                            problems_data = list(result.values())
                            print(f"Trying to use values as problems: found {len(problems_data)} items")
            elif isinstance(result, list):
                problems_data = result
            else:
                raise PolygonException(
                    f"Invalid result format: expected dict or list, got {type(result)}"
                )
            
            if not isinstance(problems_data, list):
                raise PolygonException(
                    f"Invalid problems data format: expected list, got {type(problems_data)}"
                )
            
            print(f"Found {len(problems_data)} problem(s) in data")
            print("Processing problem data...")
            problems = []
            for i, prob_data in enumerate(problems_data):
                try:
                    print(f"Processing problem {i+1}/{len(problems_data)}")
                    if not isinstance(prob_data, dict):
                        print(f"Skipping problem {i+1} - not a dictionary: {type(prob_data)}")
                        continue
                        
                    # 添加题目编号（如果是字母编号格式）
                    if isinstance(result, dict) and all(len(key) == 1 and key.isupper() for key in result.keys()):
                        for letter, data in result.items():
                            if data is prob_data:
                                prob_data = dict(prob_data)  # 创建副本以避免修改原始数据
                                prob_data["contestLetter"] = letter
                                break
                    
                    print(f"Problem data: {prob_data}")
                    problem = Problem.from_dict(prob_data)
                    problems.append(problem)
                except Exception as ex:
                    print(f"Error processing problem {i+1}: {str(ex)}")
                    continue
                    
            # 按题目编号排序（如果有）
            problems.sort(key=lambda p: getattr(p, "contestLetter", "Z"))
            print("Problem data processing completed")
            print(f"Successfully processed {len(problems)} problem(s)")
                
            return problems
            
        except Exception as e:
            print(f"Exception in get_problems: {str(e)}")
            raise PolygonException(f"Failed to get contest problems: {str(e)}")
            
    def __str__(self) -> str:
        """返回比赛会话的字符串表示"""
        return f"ContestSession(id={self.contest_id})"
        
    def __repr__(self) -> str:
        """返回比赛会话的详细字符串表示"""
        return f"ContestSession(contest_id={self.contest_id}, pin={'***' if self.pin else 'None'})" 