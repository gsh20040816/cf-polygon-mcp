# Changelog

本项目的发布记录按版本整理，重点记录新增工具、修复问题和兼容性变更。

## [Unreleased]

- 暂无未发布变更。

## [0.12.1] - 2026-03-07

### Added

- 新增 `CHANGELOG.md`，开始按版本维护发布记录。

### Changed

- `publish.yml` 在发布前会校验 `CHANGELOG.md` 中存在当前版本条目。
- README 的自动发版流程增加 changelog / release notes 约定。

## [0.12.0] - 2026-03-07

### Added

- 新增 `download_problem_package_info(problem_id, package_id, ...)`。
- 下载类 `_info` 接口统一补充 `source_kind`、`source_ref`、`filename`、`content_kind`、`size_bytes`、`sha256` 等固定字段。

### Changed

- 二进制下载接口统一分为“原始 bytes 下载”和“`_info` 元数据返回”两族。
- `download_problem_package` 被归类到 `downloads` 工具分组。

## [0.11.0] - 2026-03-07

### Changed

- 系统性整理 MCP tool 的 docstring，统一参数含义、返回结构和读写/workflow 分类说明。
- README 增补面向 agent 的调用约束与下载接口约定。

## [0.10.0] - 2026-03-07

### Changed

- 最低 Python 版本要求调整为 `>=3.11`。
- GitHub Actions 改为在 Python 3.11 上安装、测试和构建。

### Fixed

- 修复发布 workflow 测试环境缺少 `setuptools` 导致的构建失败。

## [0.9.1] - 2026-03-07

### Changed

- `setuptools` 改为自动发现 `src*` 包，减少手工维护打包配置。

## [0.9.0] - 2026-03-07

### Added

- `check_problem_readiness()` 新增题面资源、测试组依赖、脚本漂移、generator 文件、主解/错误解覆盖等竞赛场景检查。

## [0.8.0] - 2026-03-07

### Added

- workflow 返回新增 `stage`、`decision`、`can_retry`、`recovery_actions`，便于上层 agent 编排恢复动作。

## [0.7.2] - 2026-03-07

### Changed

- 抽象通用 session/client 调用 helper，清理 MCP utils 中的重复样板代码。

## [0.7.1] - 2026-03-07

### Changed

- `server.py` 改为基于工具注册表驱动，并增加注册完整性测试。

## [0.7.0] - 2026-03-07

### Added

- 显式声明运行时依赖 `pydantic`。

### Changed

- 统一 MCP 写工具返回结构与敏感字段脱敏策略。
- 底层 Polygon API 请求增加异常分层、重试与退避。
