# 通用 AGENTS.md 模板

## 目的

`AGENTS.md` 是给 AI 编码助手看的行为规范，不是给人看的项目介绍。它应该告诉 AI 在这个仓库里如何读代码、如何改代码、如何验证结果、哪些事情绝对不能做。

好的 `AGENTS.md` 应该具体、可执行、可检查，避免只写抽象原则。它的目标是减少越权修改、错误假设、无关重构和不必要的返工。

## 技术栈

在这里填写项目使用的主要技术。不要写宣传性描述，只写会影响 AI 行为的事实。

```markdown
## Project Technical Stack

- Runtime:
- Language:
- Backend framework:
- Frontend framework:
- Database:
- Testing:
- Formatting/linting:
- Package manager:
- Build/deploy:
- Local development environment:
- Important generated files:
- Important local assets:
```

填写建议：

- 写清楚语言版本、框架、测试工具和格式化工具。
- 写清楚哪些文件是生成物，不应该手动编辑或提交。
- 写清楚本地模型、图片、样例数据、配置文件等特殊资产。
- 如果项目有多个子系统，分别列出。

## 代码风格

通用模板：

```markdown
## Code Style

- Follow the style already used in nearby files.
- Keep functions small and explicit.
- Prefer clear constants for repeated paths, labels, IDs, endpoints, colors, and messages.
- Prefer structured APIs over brittle string manipulation.
- Keep changes scoped to the user's request.
- Avoid unrelated refactors.
- Add comments only when they explain non-obvious decisions.
- Preserve existing public behavior unless the user explicitly asks for behavior changes.
- Document new runtime dependencies in the appropriate dependency file.
```

根据项目定制：

- Python 项目：说明是否使用 `black`、`flake8`、`pytest`、`pathlib`、类型标注。
- JavaScript/TypeScript 项目：说明缩进、引号、分号、ESLint、Prettier、测试命令。
- 前端项目：说明设计系统、组件库、响应式要求和浏览器验证方式。
- 数据或模型项目：说明数据路径、模型权重、输出目录和禁止下载/覆盖的资产。
- 多语言项目：按语言分别写规则，避免让 AI 猜。

## AI 编码规则

```markdown
## AI Coding Rules

- Read the relevant source and config files before editing.
- Keep changes scoped to the user's request.
- Do not make changes beyond the specific scope described in the user's request, even if other improvements are possible.
- When in doubt about the scope of a change, ask the user before proceeding.
- Do not delete any comments unless the user explicitly requests it.
- Preserve existing public behavior unless the user explicitly asks for a behavior change.
- Do not rewrite unrelated UI, business logic, dependencies, generated files, or configuration.
- If existing user changes are present, do not revert them unless explicitly requested.
- If a requested change requires touching files outside the stated scope, explain why and ask first.
- Keep secrets, API keys, tokens, and credentials out of source files and logs.
- Run the smallest relevant verification command after changes.
- If verification cannot be run, say why.
```

今天实验发现的关键规则：

- 不得删除注释，除非用户明确要求。
- 不得超出用户指令范围，即使其他改进看起来有价值。
- 范围不确定时先问用户，不要擅自扩大修改。

## 禁止事项

通用模板：

```markdown
## Prohibited Actions

- Do not commit secrets, API keys, `.env` files, logs, generated outputs, or private data.
- Do not delete comments unless the user explicitly requests it.
- Do not make changes beyond the specific scope described in the user's request.
- Do not run destructive Git commands such as `git reset --hard` or `git checkout --` unless explicitly requested.
- Do not remove local assets, fixtures, model weights, sample data, or user-created files unless explicitly requested.
- Do not introduce network calls during startup unless the user explicitly asks for that behavior.
- Do not add heavyweight dependencies or frameworks without user approval.
- Do not change public APIs, endpoints, prompts, model names, auth flows, or persistence behavior silently.
- Do not modify files outside the current project unless the user explicitly asks for it.
- When in doubt about scope, ask the user before proceeding.
```

根据项目补充：

- 对模型项目，禁止下载或替换权重。
- 对前端项目，禁止引入新框架或重写设计系统。
- 对 API 项目，禁止改变认证、端点、请求格式或兼容性。
- 对生产项目，禁止跳过测试、迁移或安全检查。
- 对包含生成物的项目，禁止提交输出文件。

## 使用说明

1. 把本模板复制为项目根目录的 `AGENTS.md`。
2. 先填写技术栈，确保 AI 知道项目真实工具链。
3. 根据项目已有代码风格改写 `Code Style`，不要只保留通用描述。
4. 保留 `AI Coding Rules` 中的范围控制规则，尤其是不得删除注释、不得越权、不确定先问。
5. 根据项目风险补充 `Prohibited Actions`。
6. 添加项目常用验证命令，例如测试、lint、格式检查和构建命令。
7. 如果仓库有子目录使用不同规则，在子目录再放一个更具体的 `AGENTS.md`。
8. 每次发现 AI 重复犯错时，把可复用规则补进 `AGENTS.md`。
9. 保持规则短、具体、可执行；删除空泛口号。

维护建议：

- 把 `AGENTS.md` 当作 AI 的操作手册，而不是 README。
- 优先写“必须做什么”和“不能做什么”。
- 每条规则最好能通过 diff、测试或人工审核判断是否遵守。
- 项目变化后及时更新规则，避免旧规则误导 AI。
