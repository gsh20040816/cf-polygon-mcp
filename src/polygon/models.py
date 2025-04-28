from pydantic import BaseModel
from typing import Optional, Dict, TypeVar, Generic
from enum import Enum
from datetime import datetime

class AccessType(str, Enum):
    """题目访问权限类型"""
    READ = "READ"
    WRITE = "WRITE"
    OWNER = "OWNER"

class SourceType(str, Enum):
    """源文件类型"""
    SOLUTION = "solution"  # 解决方案
    VALIDATOR = "validator"  # 验证器
    CHECKER = "checker"  # 检查器
    INTERACTOR = "interactor"  # 交互器
    MAIN = "main"  # 主文件

class ResourceAdvancedProperties(BaseModel):
    """资源文件的高级属性"""
    # 根据实际API返回补充字段
    pass

class File(BaseModel):
    """
    表示一个资源、源代码或辅助文件
    
    Attributes:
        name: 文件名
        modificationTimeSeconds: 文件修改时间（Unix时间戳）
        length: 文件长度（字节）
        sourceType: 源文件类型（仅对源文件有效）
        resourceAdvancedProperties: 资源文件的高级属性（可选）
    """
    name: str
    modificationTimeSeconds: datetime
    length: int
    sourceType: Optional[SourceType] = None
    resourceAdvancedProperties: Optional[ResourceAdvancedProperties] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "File":
        """从API响应数据创建File实例"""
        # 转换时间戳为datetime对象
        if "modificationTimeSeconds" in data:
            data["modificationTimeSeconds"] = datetime.fromtimestamp(
                int(data["modificationTimeSeconds"])
            )
        
        # 如果存在sourceType，转换为枚举
        if "sourceType" in data:
            data["sourceType"] = SourceType(data["sourceType"])
            
        # 如果存在resourceAdvancedProperties，创建对象
        if "resourceAdvancedProperties" in data and data["resourceAdvancedProperties"]:
            data["resourceAdvancedProperties"] = ResourceAdvancedProperties(
                **data["resourceAdvancedProperties"]
            )
            
        return cls(**data)

class PolygonException(Exception):
    """Polygon API 异常基类"""
    pass

class AccessDeniedException(PolygonException):
    """访问权限不足异常"""
    pass

T = TypeVar('T')

class LanguageMap(BaseModel, Generic[T]):
    """
    语言到特定类型的映射
    
    用于表示不同语言版本的内容，如题目描述、题解等
    """
    items: Dict[str, T]
    
    @classmethod
    def from_dict(cls, data: dict, item_class) -> "LanguageMap[T]":
        """从API响应数据创建LanguageMap实例"""
        return cls(
            items={
                lang: item_class.from_dict(item_data)
                for lang, item_data in data.items()
            }
        )
    
    def __getitem__(self, key: str) -> T:
        """通过语言代码获取对应的内容"""
        return self.items[key]
    
    def get(self, key: str, default: Optional[T] = None) -> Optional[T]:
        """安全地获取指定语言的内容"""
        return self.items.get(key, default)
    
    def keys(self):
        """获取所有可用的语言代码"""
        return self.items.keys()
    
    def values(self):
        """获取所有语言版本的内容"""
        return self.items.values()
    
    def items(self):
        """获取所有(语言代码, 内容)对"""
        return self.items.items()

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

class Statement(BaseModel):
    """
    表示题目的陈述/描述
    
    Attributes:
        encoding: 陈述的编码格式
        name: 该语言下的题目名称
        legend: 题目描述
        input: 输入格式说明
        output: 输出格式说明
        scoring: 评分说明
        interaction: 交互协议说明（仅用于交互题）
        notes: 题目注释
        tutorial: 题解
    """
    encoding: str
    name: str
    legend: str
    input: str
    output: str
    scoring: Optional[str] = None
    interaction: Optional[str] = None
    notes: Optional[str] = None
    tutorial: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> "Statement":
        """从API响应数据创建Statement实例"""
        return cls(
            encoding=data["encoding"],
            name=data["name"],
            legend=data["legend"],
            input=data["input"],
            output=data["output"],
            scoring=data.get("scoring"),
            interaction=data.get("interaction"),
            notes=data.get("notes"),
            tutorial=data.get("tutorial")
        )