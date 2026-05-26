<!--
Function Name: docs-maintenance-checklist.zh-cn
Description: agent-workflows 文档维护清单中文翻译。
-->

# 文档维护清单

## 交叉引用检查

- README 列出每一个工作流、共享文档和内置技能。
- 仓库结构块与实际文件一致。
- Markdown 链接和标题锚点都能正确解析。
- 工作流路由参考与实际工作流文件名一致。
- 库加载参考与实际共享文档和脚本一致。
- 每个可安装技能都只有一个规范的 `agents/interface.yaml`。
- 不存在遗留的按代理拆分文件，例如 `agents/openai.yaml` 和 `agents/claude.yaml`。
- 技能默认提示词提到了字面量 `$skill-name`。

## 内容检查

- 在仓库说明要求时，新文件包含函数名和说明头部。
- 重复样板内容已移动到 `shared/`，而不是到处复制。
- 工作流专属指导保留在对应工作流文件中。
- 安全规则与 `shared/safety-rules.md` 保持一致。
- 示例明确使用占位符，不虚构已执行的结果。

## 最终检查

- 运行 workflow-maintainer 审计。
- 运行受影响的辅助脚本。
- 说明改了哪些文档、运行了哪些命令、跳过了哪些验证，以及是否执行了提交或推送。
