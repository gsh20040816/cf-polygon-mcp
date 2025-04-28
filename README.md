# CF-Polygon-MCP

基于 MCP (Model API Control Protocol) 的 Codeforces Polygon API 工具集。提供了一系列便捷的工具函数来操作和管理 Polygon 平台上的题目。

## 功能特性

- 获取题目列表，支持多种筛选条件
- 获取题目详细信息（时限、内存限制等）
- 使用环境变量管理 API 密钥，安全可靠

## 安装

1. 确保你的 Python 版本 >= 3.13
2. 克隆仓库：
```bash
git clone https://github.com/gsh20040816/cf-polygon-mcp.git
cd cf-polygon-mcp
```

3. 安装依赖：
```bash
uv sync
```

## 配置

在使用之前，你需要设置 Polygon API 密钥。你可以在 [Polygon 设置页面](https://polygon.codeforces.com/settings) 获取 API Key 和 Secret。

将以下环境变量添加到你的 shell 配置文件（如 `~/.bashrc` 或 `~/.zshrc`）中：

```bash
export POLYGON_API_KEY=your_key
export POLYGON_API_SECRET=your_secret
```

## 使用方法

### 启动服务

```bash
uv run main.py
```

### 获取题目列表

支持以下筛选条件：
- `show_deleted`: 是否显示已删除的题目
- `problem_id`: 按题目ID筛选
- `name`: 按题目名称筛选
- `owner`: 按题目所有者筛选

示例：
```python
problems = get_problems(
    show_deleted=False,
    name="Two Sum",
    owner="tourist"
)
```

返回的题目信息包含：
- `id`: 题目ID
- `owner`: 题目所有者的handle
- `name`: 题目名称
- `deleted`: 题目是否已删除
- `favourite`: 题目是否在用户的收藏夹中
- `accessType`: 用户对此题目的访问权限类型（READ/WRITE/OWNER）
- `revision`: 当前题目版本号
- `latestPackage`: 最新的可用包版本号
- `modified`: 题目是否被修改

### 获取题目详细信息

通过题目ID获取题目的详细配置信息：

```python
info = get_problem_info(problem_id=1234)
```

返回的信息包含：
- `inputFile`: 题目的输入文件名
- `outputFile`: 题目的输出文件名
- `interactive`: 是否为交互题
- `timeLimit`: 时间限制（毫秒）
- `memoryLimit`: 内存限制（MB）

## 开发

项目使用 pyproject.toml 管理依赖。主要依赖：
- mcp[cli] >= 1.6.0
- requests >= 2.32.3

## 许可证

[AGPL-3.0-or-later](LICENSE)
