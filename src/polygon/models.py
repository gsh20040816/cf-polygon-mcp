from pydantic import BaseModel
from typing import Optional, Dict, TypeVar, Generic, Union
from enum import Enum
from datetime import datetime

class AccessType(str, Enum):
    """题目访问权限类型"""
    READ = "READ"
    WRITE = "WRITE"
    OWNER = "OWNER"

class FileType(str, Enum):
    """文件类型"""
    RESOURCE = "resource"  # 资源文件
    SOURCE = "source"     # 源代码文件
    AUX = "aux"          # 辅助文件

class SourceType(str, Enum):
    """源文件类型"""
    SOLUTION = "solution"  # 解决方案
    VALIDATOR = "validator"  # 验证器
    CHECKER = "checker"  # 检查器
    INTERACTOR = "interactor"  # 交互器
    MAIN = "main"  # 主文件

class SolutionTag(str, Enum):
    """
    解决方案标签
    
    Attributes:
        MA: 主要解法（Main solution）
        OK: 正确解法（Accepted）
        RJ: 会被评测系统拒绝的解法（Rejected）
        TL: 超时解法（Time Limit Exceeded）
        TO: 解法可能超时也可能通过（Time limit exceeded OR Accepted）
        WA: 错误答案解法（Wrong Answer）
        PE: 格式错误解法（Presentation Error）
        ML: 超内存解法（Memory Limit Exceeded）
        RE: 运行时错误解法（Runtime Error）
    """
    MA = "MA"  # Main solution
    OK = "OK"  # Accepted
    RJ = "RJ"  # Rejected
    TL = "TL"  # Time Limit Exceeded
    TO = "TO"  # Time limit exceeded OR Accepted
    WA = "WA"  # Wrong Answer
    PE = "PE"  # Presentation Error
    ML = "ML"  # Memory Limit Exceeded
    RE = "RE"  # Runtime Error

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

class Solution(BaseModel):
    """
    表示题目的解决方案
    
    Attributes:
        name: 解决方案文件名
        modificationTimeSeconds: 修改时间（Unix时间戳）
        length: 文件长度（字节）
        sourceType: 源文件类型（必须是'solution'）
        tag: 解决方案标签，表示这个解法的类型和预期结果
    """
    name: str
    modificationTimeSeconds: datetime
    length: int
    sourceType: SourceType = SourceType.SOLUTION
    tag: SolutionTag
    
    @classmethod
    def from_dict(cls, data: dict) -> "Solution":
        """从API响应数据创建Solution实例"""
        # 转换时间戳为datetime对象
        if "modificationTimeSeconds" in data:
            data["modificationTimeSeconds"] = datetime.fromtimestamp(
                int(data["modificationTimeSeconds"])
            )
            
        # 确保sourceType是solution
        data["sourceType"] = SourceType.SOLUTION
        
        # 转换tag为枚举
        if "tag" in data:
            data["tag"] = SolutionTag(data["tag"])
            
        return cls(**data)
    
    def is_correct(self) -> bool:
        """
        判断是否为正确解法
        
        Returns:
            bool: 如果是MA（主要解法）或OK（正确解法）则返回True
        """
        return self.tag in (SolutionTag.MA, SolutionTag.OK)
    
    def is_wrong(self) -> bool:
        """
        判断是否为错误解法
        
        Returns:
            bool: 如果不是正确解法且不是TO（可能正确可能超时）则返回True
        """
        return not (self.is_correct() or self.tag == SolutionTag.TO)
    
    def is_uncertain(self) -> bool:
        """
        判断是否为结果不确定的解法
        
        Returns:
            bool: 如果是TO（可能正确可能超时）则返回True
        """
        return self.tag == SolutionTag.TO
    
    def get_verdict(self) -> str:
        """
        获取解法的预期判定结果
        
        Returns:
            str: 人类可读的预期判定结果
        """
        tag_verdicts = {
            SolutionTag.MA: "Accepted (Main)",
            SolutionTag.OK: "Accepted",
            SolutionTag.RJ: "Rejected",
            SolutionTag.TL: "Time Limit Exceeded",
            SolutionTag.TO: "Time Limit Exceeded or Accepted",
            SolutionTag.WA: "Wrong Answer",
            SolutionTag.PE: "Presentation Error",
            SolutionTag.ML: "Memory Limit Exceeded",
            SolutionTag.RE: "Runtime Error"
        }
        return tag_verdicts[self.tag]

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
        contestLetter: 题目在比赛中的编号（A, B, C...），可选
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
    contestLetter: Optional[str] = None  # 题目在比赛中的编号
    
    @classmethod
    def from_dict(cls, data: dict) -> "Problem":
        """
        从API响应数据创建Problem实例
        
        Args:
            data: API返回的题目数据字典
            
        Returns:
            Problem: 题目对象
            
        Raises:
            ValueError: 当必需的字段缺失或格式不正确时
        """
        try:
            # 确保必需的字段存在
            required_fields = ["id", "name", "owner"]
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                print(f"Warning: Missing required fields: {', '.join(missing_fields)}")
                print(f"Available fields: {', '.join(data.keys())}")
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
            
            # 转换数据类型
            problem_data = {
                "id": int(data["id"]),
                "name": str(data["name"]),
                "owner": str(data["owner"]),
                "deleted": bool(data.get("deleted", False)),
                "favourite": bool(data.get("favourite", False)),
                "modified": bool(data.get("modified", False))
            }
            
            # 处理访问权限类型，使用默认值READ如果不存在
            access_type = data.get("accessType", "READ")
            try:
                problem_data["accessType"] = AccessType(access_type)
            except ValueError:
                print(f"Warning: Invalid accessType '{access_type}', defaulting to READ")
                problem_data["accessType"] = AccessType.READ
            
            # 处理可选字段
            if "revision" in data:
                problem_data["revision"] = int(data["revision"])
            if "latestPackage" in data:
                problem_data["latestPackage"] = int(data["latestPackage"])
            if "contestLetter" in data:
                problem_data["contestLetter"] = str(data["contestLetter"])
                
            return cls(**problem_data)
            
        except Exception as e:
            print(f"Error in Problem.from_dict: {str(e)}")
            # 打印数据以便于调试
            print(f"Problematic data: {data}")
            raise ValueError(f"Failed to create Problem object: {str(e)}")
            
    def __str__(self) -> str:
        """返回题目的字符串表示"""
        if self.contestLetter:
            return f"Problem {self.contestLetter}: {self.name} (ID: {self.id})"
        return f"Problem: {self.name} (ID: {self.id})"

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