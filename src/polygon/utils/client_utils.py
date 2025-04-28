import requests
import time
import random
import hashlib
from typing import Dict, Optional, Union

def generate_api_signature(api_secret: str, method_name: str, params: Dict) -> str:
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
    signature_base += f"#{api_secret}"
    
    # 计算sha512
    sha = hashlib.sha512(signature_base.encode()).hexdigest()
    
    return f"{rand}{sha}"

def make_api_request(
    api_key: str,
    api_secret: str,
    base_url: str,
    method: str,
    params: Optional[Dict] = None,
    raw_response: bool = False
) -> Union[Dict, bytes]:
    """
    发送请求到Polygon API
    
    Args:
        api_key: API密钥
        api_secret: API密钥对应的秘钥
        base_url: API基础URL
        method: API方法名
        params: 请求参数
        raw_response: 是否返回原始响应内容
        
    Returns:
        Union[Dict, bytes]: 如果raw_response为True，返回原始响应内容；
                          否则返回解析后的JSON数据
    """
    if params is None:
        params = {}
        
    # 添加必要的参数
    params.update({
        "apiKey": api_key,
        "time": str(int(time.time())),
    })
    
    # 生成签名
    params["apiSig"] = generate_api_signature(api_secret, method, params)
    
    # 发送请求
    response = requests.get(f"{base_url}{method}", params=params)
    response.raise_for_status()
    
    # 根据需要返回原始内容或解析的JSON
    if raw_response:
        return response.content
        
    # 解析响应
    data = response.json()
    if data.get("status") != "OK":
        raise Exception(f"API request failed: {data.get('comment', 'Unknown error')}")
        
    return data 