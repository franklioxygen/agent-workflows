<!--
Function Name: workflow-routing.zh-cn
Description: 工作流自动化技能的工作流路由参考中文翻译。
-->

# 工作流路由参考

说明：把用户请求路由到正确的 `agent-workflows` 文档，并知道什么时候该在工作流之间交接。

## 主工作流选择

- `project-initialization-agent-workflow.md`
用于新项目、绿地代码库、初始仓库脚手架、初始工具链选择、包管理设置、基础 README/.gitignore/配置创建以及初始脚手架验证。

- `feature-development-agent-workflow.md`
用于新能力、产品行为变更、跨文件功能、新 API、迁移、权限、发布控制类工作，或任何需要先设计后编码的任务。

- `bug-fix-agent-workflow.md`
用于“某些东西坏了、错了、回归了或失败了”，目标是恢复正确行为的场景。

- `code-review-agent-workflow.md`
用于用户要求评审代码、Pull Request、分支或工作区变更，并且默认行为应是只读发现项输出的场景。

- `incident-debugging-agent-workflow.md`
用于生产或在线环境故障、告警、宕机、数据损坏、性能退化，或事故后的根因分析。

- `refactoring-agent-workflow.md`
用于目标是在不改变行为的前提下改进结构的场景。

- `tech-debt-cleanup-agent-workflow.md`
用于清理、删除死代码、依赖升级、处理 TODO/FIXME、技术债盘点，以及比单次重构更宽泛的通用卫生治理工作。

## 交接规则

- Incident -> Bug Fix
在事故工作流中一直处理到影响被缓解、证据被保存。如果剩余工作已经变成普通代码修复，则切到缺陷修复工作流。

- Bug Fix -> Feature
如果诊断发现问题来自设计或产品决策，而不是狭义缺陷，则切到功能工作流。

- Tech Debt -> Refactoring
如果清理任务最终收敛为某个局部区域内、保持行为不变的结构性改造，通常应改用重构工作流作为主路径。

- Tech Debt 或 Refactoring -> Feature
如果工作需要行为变更、公共契约变更或设计决策，就不要再把它当成清理或重构，应切到功能工作流。

- Code Review -> Fix
除非用户明确要求处理发现项，否则保持在评审工作流内。如果用户要求修复，且发现项暴露出功能、缺陷或重构任务，则从评审中的修复路径继续，或切换到更具体的编码工作流。

## 处理歧义

- 只有当工作流选择会实质改变你接下来采取的动作时，才提一个简短澄清问题。
- 如果歧义风险较低，选择最可能的工作流，说明假设，然后继续。
- 如果用户明确点名某个工作流，除非明显不安全，否则就使用它。
