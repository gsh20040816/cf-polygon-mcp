# CF-Polygon-MCP

基于 MCP (Model API Control Protocol) 的 Codeforces Polygon API 工具集。提供一系列便捷工具函数，用于操作和管理 Polygon 平台上的算法竞赛题目。

## 功能特性

- **题目管理**
  - 获取题目列表，支持多种筛选条件（题目ID、名称、所有者等）
  - 查看题目是否已删除、是否在收藏夹中
  - 检查用户对题目的访问权限类型（READ/WRITE/OWNER）

- **题目详情**
  - 获取题目的详细配置信息
  - 查看时间限制、内存限制
  - 确认题目是否为交互式题目
  - 获取输入输出文件名设置

- **版本控制**
  - 查看当前题目版本号
  - 获取最新可用包版本号
  - 检查题目是否被修改

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

在使用前，需要设置 Polygon API 密钥。可在 [Polygon 设置页面](https://polygon.codeforces.com/settings) 获取 API Key 和 Secret。

将环境变量添加到你的 shell 配置文件（如 `~/.bashrc` 或 `~/.zshrc`）中：

```bash
export POLYGON_API_KEY=your_key
export POLYGON_API_SECRET=your_secret
```

## 使用方法

### 启动 MCP 服务

```bash
uv run main.py
```

## 技术细节

- 基于 MCP 协议构建，提供标准化的 API 交互
- 使用环境变量安全管理 API 密钥
- 项目依赖：
  - mcp[cli] >= 1.6.0
  - requests >= 2.32.3

## 许可证

[AGPL-3.0-or-later](LICENSE)

## 说明

本项目由 AI 生成。