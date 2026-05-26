---
name: test-strategy
description: 为功能、缺陷修复、重构、迁移和评审设计高价值测试策略，通过把行为映射到覆盖矩阵、识别缺失边界场景、选择验证命令，并避免脆弱或低信号测试；当 Codex 被要求提供测试计划、覆盖矩阵、回归策略、QA 清单或验证方案时使用。
---

<!--
Function Name: test-strategy.zh-cn
Description: 规划高价值测试覆盖与验证的技能说明中文翻译。
-->

# 测试策略

## 快速开始

- 当仓库路径可用时，运行 `scripts/test_inventory.py <path>`。
- 在完成测试计划前，先阅读 [references/test-strategy-checklist.md](references/test-strategy-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 把测试映射到可观察行为，而不是实现细节。
- 先做定向验证，再在风险确实需要时扩大验证范围。
- 除非用户明确要求实现，否则不要改代码。

## 策略流程

1. 识别已经变更或计划变更的行为。
2. 列出风险区域：权限、数据形状、API 契约、UI 状态、错误、并发、迁移、性能和集成。
3. 盘点现有测试结构和命令：

```bash
python3 scripts/test_inventory.py /path/to/repo
```

4. 产出覆盖矩阵：

```markdown
| Behavior | Existing coverage | Needed test | Priority |
| --- | --- | --- | --- |
| <behavior> | covered / partial / missing | <test idea> | P0 / P1 / P2 |
```

5. 把自动化测试、手工 QA 和验证命令分开列出。
6. 标明哪些测试不应被更新，因为它们断言的是稳定行为。

## 输出规则

- 包含精确场景、输入、期望结果，以及每个测试为什么重要。
- 标记回归测试：修复前应失败，修复后应通过。
- 说明跳过的测试或验证及其原因。
- 标出弱测试：宽泛快照、恒真断言、时间敏感测试，以及与实现一一映射而不是验证行为的测试。
