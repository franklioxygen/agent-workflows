---
name: migration-planning
description: 规划安全的 schema、数据、API、契约和配置迁移，覆盖发布阶段、向后兼容、验证、回滚、数据回填和部署顺序；当 Codex 被要求设计或评审迁移、破坏性 API 变更、数据库变更、数据回填、特性开关发布或兼容性敏感版本时使用。
---

<!--
Function Name: migration-planning.zh-cn
Description: 安全迁移规划与评审技能说明中文翻译。
-->

# 迁移规划

## 快速开始

- 当仓库路径或变更路径可用时，运行 `scripts/migration_signal_scan.py <path>`。
- 在完成计划前，先阅读 [references/migration-checklist.md](references/migration-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 对数据库和公共契约优先采用 expand-contract 迁移模式。
- 未经明确许可，不要执行迁移、修改数据、部署、提交或推送。

## 规划流程

1. 识别迁移对象：schema、数据、API、事件契约、配置、依赖或运行时行为。
2. 定义兼容性要求：旧代码配合新数据、新代码配合旧数据、旧客户端配合新 API，以及回滚路径。
3. 把发布拆成多个阶段：

- Prepare：加法式变更、双读或双写、特性开关。
- Backfill：幂等、可恢复、可观测的数据变更。
- Switch：把流量或行为切换到新路径。
- Contract：只有在安全性被证明之后，才移除旧字段、旧代码、旧开关或兼容垫片。

4. 为每个阶段产出带验证和回滚方案的迁移计划。
5. 明确标记不可逆步骤，并在执行前要求批准。

## 输出规则

- 包含部署顺序和回滚顺序。
- 包含数据验证查询或检查项。
- 包含监控和告警信号。
- 包含影响面和预期耗时。
- 说明移除兼容性代码之前必须满足哪些条件。
