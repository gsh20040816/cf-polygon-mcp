# CF-Polygon-MCP

基于 Codeforces Polygon API 的 MCP 工具集，提供一系列工具函数用于管理 Polygon 平台上的题目。

## 功能特性

- 获取题目列表，支持多种筛选条件
- 获取题目详细信息（时限、内存限制等）
- 获取题目描述、题解、输入输出格式等
- 获取题目解决方案
- 获取题目验证器、检查器、交互器等
- 获取比赛题目列表

## 配置

向 mcp.json 中添加：
```json
"cf-polygon-mcp": {
	"command": "uvx",
	"args": ["cf-polygon-mcp"],
	"env": {
		"POLYGON_API_KEY": "your_key",
		"POLYGON_API_SECRET": "your_secret"
	}
}
```

在使用前，需要设置 Polygon API 密钥。可在 [Polygon 设置页面](https://polygon.codeforces.com/settings) 获取 API Key 和 Secret。

## 开发

1. 确保你已经安装了 Python 3.13 及以上版本。
2. 克隆项目：
```bash
git clone https://github.com/gsh20040816/cf-polygon-mcp.git
cd cf-polygon-mcp
```

3. 安装依赖：
```bash
uv sync
```

4. 运行项目：
```bash
uv run mcp dev main.py
```
## 许可证

[AGPL-3.0-or-later](LICENSE)

## 说明

本项目由 AI 生成。