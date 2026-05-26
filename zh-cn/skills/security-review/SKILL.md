---
name: security-review
description: 对代码变更、Pull Request、分支或工作区 diff 进行聚焦安全评审，关注认证、授权、输入校验、注入、密钥处理、敏感数据暴露、依赖风险、不安全传输和危险运维行为；当 Codex 被要求进行安全评审、威胁导向代码审查、认证/权限审查或安全风险评估时使用。
---

<!--
Function Name: security-review.zh-cn
Description: 聚焦代码变更安全评审的技能说明中文翻译。
-->

# 安全评审

## 快速开始

- 把这个技能当成聚焦型评审层，而不是正常正确性评审的替代品。
- 当仓库路径或变更文件路径可用时，运行 `scripts/security_signal_scan.py <path>`。
- 在输出发现前，先阅读 [references/security-review-checklist.md](references/security-review-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 除非用户明确要求修复，否则保持只读。
- 未经明确许可，不要提交、推送、部署、轮换密钥、吊销凭证或执行破坏性命令。

## 评审流程

1. 明确范围：

- 评审目标：PR、分支、工作区变更或具体文件。
- 如果在评审 diff，确认比较基线。
- 该变更触及的信任边界。
- 被触及的安全敏感领域：认证、权限、密钥、支付、PII、文件上传、网络调用、命令执行、数据库访问、依赖升级、日志或遥测。

2. 运行信号扫描：

```bash
python3 scripts/security_signal_scan.py /path/to/repo-or-file
```

3. 手动追踪高风险链路：

- 外部输入到危险汇点：数据库查询、shell 命令、HTML/模板渲染、文件路径、网络请求、反序列化、日志或重定向。
- 身份到授权决策：认证来源、用户/会话查找、角色/权限检查、租户或归属边界。
- 密钥从创建到存储/使用/日志记录的路径。
- 敏感数据从存储到响应、日志、分析系统或第三方调用的路径。

4. 先报告发现项，并按严重级别排序。使用下面格式：

```markdown
### [Severity] Finding title

- Location:
- Problem:
- Why it matters:
- Attack or failure scenario:
- Recommended fix:
- Severity: Critical / Major / Minor / Nit
```

5. 如果没有发现问题，要明确说明，同时列出剩余风险、跳过的检查和已执行的验证。

## 严重级别指引

- Critical：直接导致数据暴露、认证绕过、授权绕过、凭证泄漏、远程代码执行、破坏性数据修改或可利用注入。
- Major：缺少边界场景授权、存在可利用路径的不安全输入处理、敏感日志、不安全默认值、危险依赖升级或租户边界风险。
- Minor：纵深防御缺口、较弱的校验、不完整审计轨迹、含糊的安全行为或低概率暴露。
- Nit：没有实质性安全影响的命名、注释或结构问题。

## 与其他工作流协作

- 广泛代码评审用 `code-review-agent-workflow.md`；需要更深的安全视角时叠加本技能。
- 如果安全评审发现了缺陷，先报告发现项，再交接给缺陷修复工作流。
- 如果评审暴露出设计或策略决策缺口，交接给功能工作流，而不是自行发明安全策略。
