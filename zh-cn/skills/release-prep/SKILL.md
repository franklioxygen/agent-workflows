---
name: release-prep
description: 为 agent-workflows 库做发布准备，检查发布就绪性、收集变更文件、运行 workflow-maintainer 审计、起草发布说明、生成验证证据并输出最终发布清单；当 Codex 被要求准备、校验、汇总、打包或交接 agent-workflows 发布时使用。
---

<!--
Function Name: release-prep.zh-cn
Description: 准备 agent-workflows 发布的技能说明中文翻译。
-->

# 发布准备

## 快速开始

- 在此技能目录下运行 `scripts/prepare_release_report.py`，或使用其绝对路径，来收集发布输入。
- 如果该仓库里提供了 `workflow-maintainer` 技能，在起草发布说明前先运行其审计。
- 阅读 [references/release-checklist.md](references/release-checklist.md) 以获取发布判断检查项和最终交接内容。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 未经明确许可，不要创建标签、提交、推送、GitHub Release 或包上传。

## 发布流程

1. 确认仓库状态：

```bash
python3 scripts/prepare_release_report.py
```

2. 运行确定性验证：

```bash
python3 ../workflow-maintainer/scripts/audit_workflow_library.py
python3 ../workflow-automation/scripts/find_workflow_library.py --json
```

3. 检查变更文件并判断发布影响级别：

- `major`：破坏性的工作流语义变更、文件重命名、工作流移除，或不兼容的技能行为变更。
- `minor`：新增工作流、新增技能、新增检查项，或向后兼容的能力扩展。
- `patch`：错字修复、文档澄清、元数据修正、非破坏性的脚本修复。

4. 起草发布说明，包含：

- 摘要
- 面向用户的变更
- 新增或变更的技能
- 已执行的验证
- 破坏性变更（如果有）
- 迁移说明（如果有）
- 已知限制或后续事项

5. 最终交接必须明确说明是否执行了提交、打标签、推送和发布动作。除非用户明确批准，否则默认答案应为“否”。

## 维护规则

- 发布说明要基于实际观察到的变更，保持事实准确。
- 如果仓库没有定义版本规范，不要虚构版本号；应询问用户，或将本次发布标记为“未版本化草案”。
- 将失败的审计、损坏链接、必需文件缺失、README 清单过期、技能元数据无效或辅助脚本未验证视为发布阻塞项。
- 如果工作区不是 Git 仓库，则输出基于文件系统的发布报告，并明确说明无法获取 Git diff 元数据。
