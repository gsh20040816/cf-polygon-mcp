from pydantic import BaseModel
from typing import Optional
from enum import Enum

class AccessType(str, Enum):
    """题目访问权限类型"""
    READ = "READ"
    WRITE = "WRITE"
    OWNER = "OWNER"

class PolygonException(Exception):
    """Polygon API 异常基类"""
    pass

class AccessDeniedException(PolygonException):
    """访问权限不足异常"""
    pass

class ProblemInfo(BaseModel):
    """
    表示题目的基本信息
    
    Attributes:
        inputFile: 题目的输入文件名
        outputFile: 题目的输出文件名
        interactive: 是否为交互题
        timeLimit: 时间限制（毫秒）
        memoryLimit: 内存限制（MB）
    """
    inputFile: str
    outputFile: str
    interactive: bool
    timeLimit: int  # 毫秒
    memoryLimit: int  # MB
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProblemInfo":
        """从API响应数据创建ProblemInfo实例"""
        return cls(
            inputFile=data["inputFile"],
            outputFile=data["outputFile"],
            interactive=data.get("interactive", False),
            timeLimit=data["timeLimit"],
            memoryLimit=data["memoryLimit"]
        )

class Problem(BaseModel):
    """
    表示一个Polygon题目
    
    Attributes:
        id: 题目ID
        owner: 题目所有者的handle
        name: 题目名称
        deleted: 题目是否已删除
        favourite: 题目是否在用户的收藏夹中
        accessType: 用户对此题目的访问权限类型（READ/WRITE/OWNER）
        revision: 当前题目版本号
        latestPackage: 最新的可用包版本号
        modified: 题目是否被修改
    """
    id: int
    owner: str
    name: str
    deleted: bool = False
    favourite: bool = False
    accessType: AccessType  # READ/WRITE/OWNER
    revision: Optional[int] = None
    latestPackage: Optional[int] = None
    modified: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> "Problem":
        """从API响应数据创建Problem实例"""
        return cls(
            id=data["id"],
            name=data["name"],
            owner=data["owner"],
            deleted=data.get("deleted", False),
            favourite=data.get("favourite", False),
            accessType=AccessType(data["accessType"]),
            revision=data.get("revision"),
            latestPackage=data.get("latestPackage"),
            modified=data.get("modified", False)
        )