---
name: workflow-maintainer
description: 审计并维护 agent-workflows 库，检查文档漂移、Markdown 链接损坏、必需工作流文件缺失、README 清单过期、技能元数据无效，以及自动化脚本与文档不一致等问题；当 Codex 被要求审查、验证、更新或发布 agent-workflows 文档及内置技能时使用。
---

<!--
Function Name: workflow-maintainer.zh-cn
Description: 维护和审计 agent-workflows 工作流库的技能说明中文翻译。
-->

# 工作流维护者

## 快速开始

- 定位库根目录。审计脚本会自动检查 `AGENT_WORKFLOWS_ROOT`、脚本相对路径以及当前工作区。
- 在此技能目录中运行 `scripts/audit_workflow_library.py`，或使用绝对路径运行。
- 在进行维护编辑前，先阅读 [references/audit-checklist.md](references/audit-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 只修复报告出的漂移问题，或用户明确指定的维护范围。除非问题确实要求，否则不要重写工作流内容。
- 最终交付前重新运行审计脚本和所有受影响的辅助脚本。

## 维护规则

- 保持库的职责分离：工作流专属指导留在工作流文件中；重复的安全规则、预检和约定留在 `shared/` 中；技能专属路由规则留在相应技能里。
- 当工作流名称、文件名或共享文档发生变化时，要一起更新所有引用：`README.md`、`skills/workflow-automation/references/library-loading.md`、`skills/workflow-automation/references/workflow-routing.md` 以及相关脚本。
- 将损坏链接、必需文件缺失、过期的技能元数据和无效清单视为阻塞问题。
- 将纯样式改动、措辞优化和可选示例视为非阻塞，除非用户明确要求它们。
- 未经明确许可，绝不要提交或推送。

## 审计工作流

1. 运行审计脚本：

```bash
python3 scripts/audit_workflow_library.py
```

2. 如果脚本报告错误，先只检查受影响的文件。
3. 如果问题涉及人工判断，而不是确定性校验，参考清单文档。
4. 应用范围收窄的修复。
5. 重新运行：

```bash
python3 scripts/audit_workflow_library.py
python3 skills/workflow-automation/scripts/find_workflow_library.py --json
```

6. 报告已修复的问题、运行过的命令、剩余警告，以及是否跳过了任何验证。

## 何时阅读清单

当用户要求对该库进行人工评审、发布就绪性检查、文档一致性检查、路由变更检查，或脚本未报错但改动仍可能带来工作流设计风险时，阅读 [references/audit-checklist.md](references/audit-checklist.md)。
