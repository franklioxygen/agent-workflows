---
name: project-initialization
description: 使用 agent-workflows 的项目初始化工作流来启动新项目和绿地仓库；当 Codex 被要求创建新项目、初始化仓库、搭建绿地代码库、选择初始工具链、配置包管理、创建基础 README/.gitignore/配置文件或验证初始脚手架时使用。
---

<!--
Function Name: project-initialization.zh-cn
Description: 使用项目初始化工作流引导新项目的技能说明中文翻译。
-->

# 项目初始化

## 快速开始

- 找到最近的 `agent-workflows` 库。如果它不在当前工作区附近，询问 `AGENT_WORKFLOWS_ROOT` 或该库路径。
- 阅读 `project-initialization-agent-workflow.md`。
- 阅读 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md)。
- 直接应用工作流。除非用户明确要求模板，否则不要只是复述提示词。
- 在创建文件前，必须先拿到明确的目标目录。

## 执行规则

- 该技能用于新项目、绿地代码库、初始仓库脚手架和项目工具链设置。
- 把工作流文件视为预检、分诊、规划、脚手架搭建、验证和交接的唯一事实来源。
- 在分诊前先运行工作流中的预检，这样才能提前知道目标目录状态、父级工作区规则、本地说明、可用工具链以及无关本地变更。
- 对于 Minimal 项目，在确认目标目录后，用合理默认值直接搭建脚手架。
- 对于 Standard 和 Complex 项目，按工作流中的“规划 / 评审 / 搭建 / 验证 / 交接”顺序执行。
- 未经明确许可，不要提交或推送。
- 不要覆盖、回退、删除或重新格式化无关的用户变更。
- 如果目标目录缺失、有歧义，或意外地已经有内容，先停下来提问。

## 执行指引

1. 确认目标目录并检查其当前状态。
2. 加载并遵循 `project-initialization-agent-workflow.md` 中的分诊门。
3. 选择合适路径：
   - Minimal：使用 Minimal Project Prompt。
   - Standard：先收集需求，再创建/评审计划，然后搭建并验证。
   - Complex：完整执行整个工作流，并分别进行评审与验证。
4. 搭建脚手架时，让所有生成文件都留在已确认的目标目录内。
5. 使用该生态系统相关的安装、lint、类型检查、构建、测试和冒烟命令进行验证。
6. 报告创建的文件、配置的工具链、验证结果、偏差、已知限制和下一步建议。

## 参考资料

- [../../project-initialization-agent-workflow.md](../../project-initialization-agent-workflow.md)
- [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md)

## 交接

- 如果初始化后的项目已经可以进入功能开发，则交接给功能开发工作流。
- 如果验证阶段暴露出脚手架中的局部缺陷，就在该工作流内修复。
- 如果验证暴露出更大的设计或技术决策问题，则先回到项目计划，再修改脚手架。
