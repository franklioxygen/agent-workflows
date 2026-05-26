<!--
Function Name: safety-rules.zh-cn
Description: agent-workflows 工作流共享的安全规则提示词块中文翻译。
-->

# 共享安全规则

说明：`agent-workflows` 中各个工作流文档共享的、可复用的安全规则提示词块。

使用与工作流最匹配、范围最窄的规则，而不是在每个文件里重复这些内容。

<a id="standard-coding-rule"></a>

## Standard Coding Rule（标准编码规则）

用于功能开发和缺陷修复工作流。

```text
未经我明确许可，不要提交或推送。
```

<a id="review-only-rule"></a>

## Review-Only Rule（仅评审规则）

用于代码评审工作流。

```text
未经我明确许可，不要改代码、提交或推送。
```

<a id="behavior-preserving-rule"></a>

## Behavior-Preserving Rule（保持行为不变规则）

用于重构工作流。

```text
未经我明确许可，不要提交或推送。
除非我明确要求，否则不要更改可观察行为。
```

<a id="cleanup-rule"></a>

## Cleanup Rule（清理规则）

用于技术债清理工作流。

```text
未经我明确许可，不要提交或推送。
除非我明确要求，否则不要更改可观察行为。
保持每个清理单元足够小，便于独立评审和回退。
```

<a id="incident-response-rule"></a>

## Incident Response Rule（事故响应规则）

用于事故响应工作流。

```text
未经我明确许可，不要提交、推送或部署。
未经我明确许可，不要执行破坏性命令（DROP、DELETE、TRUNCATE、rm -rf、force push 等）。
```
