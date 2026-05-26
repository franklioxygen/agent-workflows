---
name: workflow-automation
description: 从 agent-workflows 库中选择并执行合适的工程工作流，覆盖项目初始化、功能开发、缺陷修复、代码评审、事故响应、重构和技术债清理；当 Codex 需要自动路由任务并直接执行对应步骤时使用。
---

<!--
Function Name: workflow-automation.zh-cn
Description: 将任务路由到正确 agent-workflows 工作流并直接执行的技能说明中文翻译。
-->

# 工作流自动化

说明：通过把任务路由到正确的工作流并直接执行对应步骤，自动化使用 `agent-workflows` 库。

## 快速开始

- 在此技能目录下运行 `scripts/find_workflow_library.py --json`，或使用脚本绝对路径运行，以定位最近的 `agent-workflows` 库并获取文件映射。
- 如果当前工作区附近找不到该库，先设置 `AGENT_WORKFLOWS_ROOT` 指向库根目录，再运行脚本。
- 阅读 [references/workflow-routing.md](references/workflow-routing.md) 来对任务分类。
- 阅读 [references/library-loading.md](references/library-loading.md) 来确定需要加载哪些共享文档和工作流文件。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 直接应用工作流。除非用户明确要求提示词模板，否则不要只是复述提示词正文。

## 执行规则

- 把工作流 Markdown 文件当作操作说明，而不是要原样转述给用户的说明文档。
- 一次只使用一个主工作流。如果任务跨越工作流边界，先完成或暂停当前工作流，再明确交接到下一个工作流。
- 如果用户明确指定了某个工作流，应尊重该要求；只有在明显不安全或不匹配时才覆盖，并解释原因。
- 保持上下文精简：加载 `README.md`、相关共享文档和选中的工作流文件即可。不要把所有工作流文件都读进来。
- 对会改代码的工作流，在仓库中直接执行对应步骤，包括验证和最终汇报。
- 对代码评审或仅调查式清理这类只读工作流，除非用户明确要求编辑，否则保持只读。

## 任务路由

当正确工作流不明显时，阅读 [references/workflow-routing.md](references/workflow-routing.md)。默认映射如下：

- 新能力、设计变更或产品行为变更：功能工作流。
- 新项目、绿地代码库、仓库脚手架或初始工具链搭建：项目初始化工作流。
- 现有行为错误或回归：缺陷修复工作流。
- 用户要求 review、findings、PR review 或 diff review：代码评审工作流。
- 线上或刚发生的生产故障、缓解、告警或事故：事故工作流。
- 目标是在不改变行为的前提下改善结构：重构工作流。
- 清理、依赖升级、删除死代码、处理 TODO 或技术债盘点：技术债清理工作流。

如果分类存在实质性歧义，提一个简短澄清问题即可。如果歧义风险较低，选择最可能的工作流并说明你的假设。

## 定位工作流库

- 先运行 `scripts/find_workflow_library.py --json`，必要时相对当前技能目录解析脚本路径。
- 该脚本会依次检查 `AGENT_WORKFLOWS_ROOT`、脚本相对路径，再从起始路径向上查找。
- 如果脚本找到了库根目录，就直接使用它返回的路径。
- 如果没有找到库，不要猜测，直接向用户询问 `agent-workflows` 的路径。

## 执行工作流

- 打开文件前先阅读 [references/library-loading.md](references/library-loading.md)。
- 运行工作流中的预检、安全规则、分诊门，以及当前任务真正需要的步骤。
- 同时遵守库里的共享约定和工作流专属规则。
- 处理事故时，优先缓解影响，并把破坏性操作视为需要批准的动作。
- 处理评审任务时，以“先给发现项”为默认方式，除非用户明确要求，否则不要编辑。

## 参考资料

- [references/workflow-routing.md](references/workflow-routing.md)
- [references/library-loading.md](references/library-loading.md)
- [scripts/find_workflow_library.py](../../../skills/workflow-automation/scripts/find_workflow_library.py)
