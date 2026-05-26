---
name: performance-review
description: 对代码变更、Pull Request、分支或工作区 diff 进行聚焦性能评审，关注算法复杂度、数据库查询模式、N+1 风险、分页、缓存、批处理、内存使用、同步 I/O、延迟和负载行为；当 Codex 被要求做性能评审、可扩展性评审、性能剖析计划、基准测试计划或延迟风险评估时使用。
---

<!--
Function Name: performance-review.zh-cn
Description: 聚焦性能评审与性能剖析规划技能说明中文翻译。
-->

# 性能评审

## 快速开始

- 当仓库路径或变更文件路径可用时，运行 `scripts/performance_signal_scan.py <path>`。
- 在输出发现前，先阅读 [references/performance-review-checklist.md](references/performance-review-checklist.md)。
- 遵循 [../_shared/references/skill-operating-rules.md](../_shared/references/skill-operating-rules.md) 中共享的安全、验证和范围规则。
- 关注热点路径、数据规模、请求速率和运维成本。
- 除非用户明确要求修复，否则保持只读。

## 评审流程

1. 先明确预期规模：记录数、每秒请求数、并发度、负载大小、内存预算和延迟预算。
2. 识别热点路径和高成本依赖：数据库、网络、文件系统、CPU、序列化、渲染、队列。
3. 运行信号扫描：

```bash
python3 scripts/performance_signal_scan.py /path/to/repo-or-file
```

4. 针对现实中的最坏输入，追踪循环、查询、API 调用和分配路径。
5. 推荐验证方式：定向测试、性能剖析、explain plan、基准测试、压测或生产指标观察。

## 输出规则

- 每个发现都必须包含规模假设和成本机制。
- 区分“已经测量到的问题”和“合理推断的风险”。
- 优先给出具体缓解措施：加分页、批量调用、加索引、带失效机制的缓存、流式处理数据、避免重复工作。
- 如果没有发现问题，也要说明剩余风险，以及是否跳过了性能剖析或基准测试。
