# cf-polygon-mcp TODO

> 目标：把仓库从“功能较全的 Polygon MCP 封装”打磨成“稳定、可预测、适合辅助算法竞赛出题工作流”的工具。

## P0 - 优先立即处理

### 1. 补全运行时依赖声明
- [x] 在 `pyproject.toml` 中显式加入 `pydantic`
- [x] 检查是否还有其他隐式依赖未声明
- [x] 本地创建全新虚拟环境验证可安装性

**验收标准**
- `uv sync` / `pip install .` 在干净环境中可成功安装
- 运行测试不依赖上游传递依赖

---

### 2. 统一 MCP 工具返回风格
- [x] 约定所有写操作工具统一返回结构化 `dict`
- [x] 明确固定字段：`status` / `action` / `message` / `result` / `error` / `error_type`
- [x] 清理当前“有的直接返回对象、有的抛异常、有的返回 dict”的混合风格
- [x] 为二进制下载类工具定义一致行为（返回 `bytes` 还是 metadata + content 分离）

**验收标准**
- 所有写操作工具返回结构一致
- 上层 agent 可不依赖特判处理大多数工具调用结果

---

### 3. 禁止回显敏感信息
- [x] 检查所有 `build_operation_result(...)` 调用点
- [x] 不再在返回结果中包含 `pin`
- [x] 建立敏感字段黑名单：`pin` / `password` / `api_secret` / `apiSig`
- [x] 如必须保留字段名则统一脱敏

**验收标准**
- 所有工具输出中不出现明文 `pin` / 密码 / secret
- 测试覆盖敏感字段不回显

---

### 4. 强化底层 API 错误处理
- [x] 在 `src/polygon/utils/client_utils.py` 中避免原地修改传入 `params`
- [x] 定义明确异常类型：网络错误 / HTTP 错误 / Polygon 业务错误 / 权限错误
- [x] 将当前泛化 `Exception` 替换为自定义异常层次
- [x] 对 429 / 502 / 503 / 504 增加可配置重试与退避
- [x] 完善错误消息，保留 Polygon comment/context

**验收标准**
- 出错时可区分错误类别
- 临时网络抖动不会立即导致工作流整体失败
- 测试覆盖常见失败路径

---

## P1 - 稳定性与可维护性提升

### 5. 为核心 workflow 补系统测试
- [x] 为 `check_problem_readiness()` 编写多场景测试
- [x] 为 `build_problem_package_and_wait()` 编写成功 / 失败 / 超时 / 无 packageId 测试
- [x] 为 `prepare_problem_release()` 编写 update 失败 / readiness 阻塞 / build 失败 / commit 失败测试
- [x] 覆盖 warnings / force / allow_warnings 分支

**验收标准**
- 核心 workflow 具备完整回归测试
- 修改工作流逻辑时能及时发现破坏性变更

---

### 6. 建立统一的 FakeProblemSession 测试基座
- [x] 抽出 `FakeProblemSession`
- [x] 支持伪造 `get_info/get_tests/get_solutions/get_packages/...`
- [x] 用假会话替换大量零散 mock 链
- [x] 为 readiness / release 类测试复用该基座

**验收标准**
- workflow 测试不再严重依赖复杂 patch
- 测试更贴近真实出题场景

---

### 7. 将 `server.py` 改为注册表驱动
- [x] 将手工 `mcp.tool()(...)` 改为列表注册
- [x] 按模块分组：read / write / workflow / downloads
- [x] 增加工具清单自检，避免新增工具忘记注册
- [ ] 让 README 可从注册表自动生成工具列表（可选）

**验收标准**
- 新增工具时只需改一个注册表
- 工具注册遗漏更容易被发现

---

### 8. 清理 MCP utils 中重复样板代码
- [x] 抽象会话获取与调用共性逻辑
- [x] 抽象 enum 解析与参数规范化逻辑
- [x] 减少“打开 session -> 调方法 -> 原样返回”的重复模板
- [x] 统一 docstring 与参数风格

**验收标准**
- 新工具实现代码显著缩短
- 不同 utils 的行为更一致

---

## P1.5 - 面向算法竞赛出题场景的增强

### 9. 增强 readiness 检查项
- [x] 检查题面引用资源是否存在
- [x] 检查交互题 / 非交互题与 `interaction` / `interactor` / `checker` 的一致性
- [x] 检查测试组依赖是否成环
- [x] 检查带分测试是否缺少 `scoring`
- [x] 检查样例是否完整展示输入输出
- [x] 检查主解数量与错误解覆盖情况
- [x] 检查 generator 脚本与相关文件是否一致

**验收标准**
- readiness 输出能更贴近真实出题审题流程
- 对竞赛题常见配置错误有更高发现率

---

### 10. 为 workflow 返回添加恢复语义
- [x] 在 workflow 结果中增加 `stage`
- [x] 增加 `decision`
- [x] 增加 `can_retry`
- [x] 增加 `recovery_actions`
- [x] 为 agent 调用设计更明确的下一步建议

**验收标准**
- 上层 agent 可根据结构化结果自动决定下一步动作
- 失败结果不仅说明“错了”，还能说明“怎么补”

---

## P2 - 工程化优化

### 11. 改进 package 发现与构建配置
- [x] 避免在 `pyproject.toml` 中手工维护全部包列表
- [x] 使用 setuptools 自动发现包
- [x] 检查当前 `src` 作为包名的布局是否需要整理
- [x] 保证新增子包无需手工补配置

**验收标准**
- 新增包不会因漏配导致发布缺文件
- 打包配置更稳健

---

### 12. 评估 Python 最低版本要求
- [x] 评估是否真的必须 `>=3.13`
- [x] 若无硬依赖，考虑降到 `>=3.10` 或 `>=3.11`
- [x] 在 CI 中验证目标最低版本

**验收标准**
- 最低版本要求有明确依据
- 降低用户使用门槛且不牺牲必要特性

---

### 13. 调整自动发布策略
- [x] 将“push 到 main 即可能发布 PyPI”改为更稳妥策略
- [x] 拆分 `ci.yml` 与 `publish.yml`
- [x] 使用 tag / release 触发 PyPI 发布
- [x] 保留 main 分支测试与构建检查

**验收标准**
- 普通合并不会自动发版
- PyPI 发布具有明确人工或 tag 控制

---

## P3 - 使用体验与文档

### 14. 补充面向出题人的文档
- [x] 增加“典型出题工作流”示例
- [x] 增加“从新建题目到 readiness/build/release”的完整链路示例
- [x] 记录交互题、带分题、测试组题目的常见操作
- [x] 增加错误排查章节

**验收标准**
- 新用户可以按文档走完整个出题流程
- 典型用法覆盖普通题 / 交互题 / 带分题

---

### 15. 为 agent 使用优化工具描述
- [x] 审核所有 tool 的 docstring
- [x] 明确参数含义、可选值、返回结构
- [x] 标注哪些工具是“读”、哪些是“写”、哪些是“workflow”
- [x] 标注调用前置条件（如需要 validator / testset / pin）

**验收标准**
- 上层 LLM/agent 更容易正确调用工具
- 减少参数误用和错误编排

---

## 可选增强

### 16. 为二进制内容提供更友好的接口设计
- [x] 统一“直接返回 bytes”与“返回 metadata”的接口族
- [x] 设计 `_info` 与原始下载接口的命名规范
- [x] 明确 statement/pdf/xml/package 的返回约定

### 17. 增加 changelog / release notes 机制
- [x] 建立 `CHANGELOG.md`
- [x] 每次发布记录新增工具、修复问题、兼容性变更

---

## P4 - 更像真实出题助手的下一阶段增强

### 18. 增加本地工程与 Polygon 双向同步
- [ ] 约定标准本地题目目录结构（statement / solutions / files / tests / scripts）
- [ ] 支持从本地目录批量导入/更新题面、source、resource、solution、test script
- [ ] 支持远端 working copy 与本地目录的 diff / dry-run 预览
- [ ] 支持按文件类型或变更集做增量同步

**验收标准**
- 维护题目时不需要手动逐个调用保存接口
- agent 能先看 diff 再同步，降低误覆盖风险

---

### 19. 补自动化验题 / 对拍 / 弱数据发现能力
- [ ] 集成本地编译主解、暴力解、错误解、generator、checker/validator 的能力
- [ ] 提供一键 smoke test / stress test / differential test workflow
- [ ] 自动定位首个反例，并可回填为额外测试或样例候选
- [ ] 根据运行结果给出“错误解覆盖不足 / 数据强度不足”的提示

**验收标准**
- 在上传 Polygon 前就能发现大量弱数据与错误解漏杀问题
- 出题人能直接拿到可复现的失败用例

---

### 20. 增加 contest 级批量编排与总览
- [ ] 按 contest 批量跑 readiness / build / release 预检
- [ ] 输出多题 dashboard：状态、阻塞项、warnings、最近 package 状态
- [ ] 检查题目之间的命名、语言、时限、交互类型、评分模式是否一致
- [ ] 支持 `stop-on-error` 与 `continue-on-error` 两种批处理策略

**验收标准**
- 能管理整场比赛而不是只盯单题
- 出题团队可快速看到全场收口状态

---

### 21. 增加审题报告与修复建议生成
- [ ] 将 readiness 结果整理成更适合审题人的 Markdown 报告
- [ ] 输出按优先级排序的修复清单，而不只是平铺 warnings
- [ ] 对“缺样例 / 缺 scoring / 缺 checker 测试 / 缺英文题面”等场景生成具体修复建议
- [ ] 支持导出给非技术审题人的简版报告

**验收标准**
- 审题人与出题人可以共享同一份结构化问题清单
- agent 输出从“能发现问题”提升到“能组织修题过程”

---

### 22. 提供低风险自动修复与题型模板
- [ ] 为普通题 / 交互题 / 带分题 / 测试组题提供初始化模板
- [ ] 支持一键生成基础 validator/checker/interactor/solution 占位文件与默认题面骨架
- [ ] 对低风险问题提供 autofix，如补建基础 `scoring` 框架、补齐资源注册建议、生成 release 前检查清单
- [ ] 明确区分可自动修复项与必须人工确认项

**验收标准**
- 新题初始化更快
- agent 可以安全地自动完成一部分机械性工作，而不会擅自改坏题目

---

### 23. 增加题目状态快照、diff 与回滚辅助
- [ ] 为 release 前后保存题目关键信息快照（info / statements / tests / files / solutions / packages）
- [ ] 提供结构化 diff，帮助比较两次 working copy 的差异
- [ ] 为关键 workflow 增加 dry-run 模式
- [ ] 在失败结果中给出更明确的“回到哪个 revision / 重新同步什么”的建议

**验收标准**
- 发布前后的变更更容易审计
- 多人协作时更容易定位是谁改了什么，以及如何安全回退

---

## 建议迭代顺序

### Sprint 1
- [x] 补 `pydantic`
- [x] 去掉敏感信息回显
- [x] 统一返回风格
- [x] 强化 `make_api_request` 错误处理

### Sprint 2
- [x] 补 workflow 测试
- [x] 引入 `FakeProblemSession`
- [x] 改造 `server.py` 注册表

### Sprint 3
- [x] 增强 readiness
- [x] 为 workflow 加恢复语义
- [x] 改造发布策略与文档

### Sprint 4
- [ ] 本地工程与 Polygon 双向同步
- [ ] 自动化验题 / 对拍 / 弱数据发现
- [ ] 审题报告与修复建议

### Sprint 5
- [ ] contest 级批量编排与总览
- [ ] 低风险自动修复与题型模板
- [ ] 题目状态快照 / diff / dry-run

---

## Done Definition
- [x] 测试全部通过
- [x] 新增/修改逻辑有对应测试
- [x] 不回显敏感信息
- [x] README / docstring 与实现一致
- [x] 对上层 agent 来说返回结构稳定、可预测
