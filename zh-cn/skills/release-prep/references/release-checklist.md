<!--
Function Name: release-checklist.zh-cn
Description: agent-workflows 发布说明和发布就绪性交接清单中文翻译。
-->

# 发布准备清单

## 发布阻塞项

- workflow-maintainer 审计存在错误。
- Markdown 链接或标题锚点损坏。
- README 清单没有提到新增、删除或重命名的工作流或技能。
- 技能元数据里包含占位文本，或 `$skill-name` 提示词不正确。
- 辅助脚本编译失败或基本执行失败。
- 发布说明遗漏了破坏性变更、迁移说明或验证失败信息。

## 发布说明模板

```markdown
# Release Notes

## Summary

<one-paragraph release summary>

## Changes

- <user-facing change>

## Skills

- <new or changed skill behavior>

## Validation

- `<command>`: <result>

## Breaking Changes

- None, or list each breaking change and required migration.

## Known Limitations

- None, or list follow-ups.
```

## 最终交接清单

- 已说明发布影响级别：major、minor、patch 或 unversioned draft。
- 已按用途汇总变更文件，而不是只罗列文件名。
- 已包含运行过的命令及结果。
- 已列出跳过的验证及原因。
- 已明确说明提交、打标签、推送和发布状态。
