# CF-Polygon-MCP

基于 Codeforces Polygon API 的 MCP 工具集，提供一系列工具函数用于管理 Polygon 平台上的题目。

## 功能特性

- 获取题目列表，支持多种筛选条件
- 创建新的空题目
- 获取题目详细信息（时限、内存限制等）
- 获取题目描述、题解、输入输出格式等
- 获取和保存题目陈述资源、源文件、辅助文件
- 获取和保存测试脚本、测试点、validator/checker 测试、测试组
- 获取题目解决方案
- 获取题目验证器、额外验证器、检查器、交互器，并支持设置验证器/检查器/交互器
- 获取和保存题目标签、通用描述、通用题解
- 获取历史包、下载包、构建包、提交工作副本
- 提供出题流程辅助工具，包括 readiness 检查、打包等待和发布编排
- 通过 Polygon 账号密码下载 problem package、problem.xml、contest.xml、statements.pdf
- 获取比赛题目列表
- 更新题目信息
- 更新/丢弃工作副本
- 更新题目描述

## 配置

向 mcp.json 中添加：
```json
"cf-polygon-mcp": {
	"command": "uvx",
	"args": ["cf-polygon-mcp"],
	"env": {
		"POLYGON_API_KEY": "your_key",
		"POLYGON_API_SECRET": "your_secret",
		"POLYGON_LOGIN": "your_login",
		"POLYGON_PASSWORD": "your_password"
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

5. 运行测试：
```bash
python -m unittest discover -s tests -v
```

## GitHub 自动发版

仓库包含 GitHub Actions 工作流 [publish.yml](.github/workflows/publish.yml)。当代码 `push` 到 `main` 后，工作流会：

- 使用 Python 3.13 安装依赖
- 运行 `python -m unittest discover -s tests -v`
- 构建 `sdist` 和 `wheel`
- 如果 `pyproject.toml` 中的版本尚未发布到 PyPI，则自动发布

要让自动发布生效，需要先在 PyPI 的 Trusted Publisher 中添加这个 GitHub 仓库：

- Owner: `gsh20040816`
- Repository name: `cf-polygon-mcp`
- Workflow name: `publish.yml`
- Environment name: `pypi`

## 许可证

[AGPL-3.0-or-later](LICENSE)

## 说明

本项目由 AI 生成。
