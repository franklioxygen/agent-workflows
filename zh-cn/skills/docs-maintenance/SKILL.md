---
name: docs-maintenance
description: 通过更新 README 条目、工作流文档、共享参考资料、技能文档、示例、链接、标题和跨文件一致性来维护 agent-workflows 文档；当 Codex 被要求更新文档、修复过期引用、添加示例、改善文档结构或验证 agent-workflows 文档时使用。
---

<!--
Function Name: docs-maintenance.zh-cn
Description: 维护 agent-workflows 文档和交叉引用的技能说明中文翻译。
-->

# 文档维护

## 快速开始

- 运行 `scripts/docs_inventory.py <path>` 来盘点 Markdown 文档和常见文档信号。
- 在维护当前 `agent-workflows` 仓库时，运行 `../workflow-maintainer/scripts/audit_workflow_library.py`。
- 在完成文档变更前，先阅读 [references/docs-maintenance-checklist.md](references/docs-maintenance-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 让修改严格围绕文档目标展开；不要不小心改变工作流语义。

## 维护流程

1. 识别文档变更类型：新增文档、文件重命名、工作流步骤变更、新技能、示例更新、错字修复或一致性修复。
2. 盘点文档：

```bash
python3 scripts/docs_inventory.py /path/to/agent-workflows
```

3. 更新所有受影响的交叉引用：

- README 清单和设置说明。
- 工作流路由和库加载参考。
- 技能文档以及 `agents/interface.yaml` 中的规范代理元数据提示词。
- 如果多个工作流文件里出现重复措辞，则更新共享约定。

4. 验证链接、锚点、清单和辅助脚本。
5. 报告已修改的文档、执行的验证以及任何被跳过的检查。

## 输出规则

- 优先使用精确措辞，而不是大范围重写。
- 保持现有语气和结构。
- 让示例可执行，或清楚标记为模板。
- 如果某条共享参考资料已经是规范来源，就不要再重复添加安全相关样板文字。
