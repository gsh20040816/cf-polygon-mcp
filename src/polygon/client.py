import requests
from typing import List, Dict, Optional
from .models import Problem
import time
import random
import hashlib

class PolygonClient:
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://polygon.codeforces.com/api/"
        
    def _generate_api_signature(self, method_name: str, params: Dict) -> str:
        """
        生成Polygon API签名
        
        签名规则:
        1. 生成一个6位随机数作为rand
        2. 将参数按key升序排序
        3. 拼接字符串: rand/method_name?param1=value1&param2=value2#api_secret
        4. 计算拼接字符串的sha512hex
        5. 返回rand + hex
        """
        # 生成6位随机数
        rand = str(random.randint(100000, 999999))
        
        # 按key升序排序参数
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        
        # 构建签名字符串
        signature_base = f"{rand}/{method_name}"
        if param_str:
            signature_base += f"?{param_str}"
        signature_base += f"#{self.api_secret}"
        
        # 计算sha512
        sha = hashlib.sha512(signature_base.encode()).hexdigest()
        
        return f"{rand}{sha}"
        
    def _make_request(self, method: str, params: Optional[Dict] = None) -> Dict:
        """发送请求到Polygon API"""
        if params is None:
            params = {}
            
        # 添加必要的参数
        params.update({
            "apiKey": self.api_key,
            "time": str(int(time.time())),
        })
        
        # 生成签名
        params["apiSig"] = self._generate_api_signature(method, params)
        
        # 发送请求
        response = requests.get(f"{self.base_url}{method}", params=params)
        response.raise_for_status()
        
        # 解析响应
        data = response.json()
        if data.get("status") != "OK":
            raise Exception(f"API request failed: {data.get('comment', 'Unknown error')}")
            
        return data
        
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
        params = {}
        
        # 添加可选参数
        if show_deleted is not None:
            params["showDeleted"] = "true" if show_deleted else "false"
        if problem_id is not None:
            params["id"] = str(problem_id)
        if name is not None:
            params["name"] = name
        if owner is not None:
            params["owner"] = owner
            
        response = self._make_request("problems.list", params)
        return [Problem.from_dict(prob) for prob in response.get("result", [])]
