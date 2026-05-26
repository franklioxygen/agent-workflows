<!--
Function Name: library-loading.zh-cn
Description: 工作流自动化技能的库加载参考中文翻译。
-->

# 工作流库加载参考

说明：通过只读取所选工作流真正需要的文件，高效加载 `agent-workflows` 库。

## 加载顺序

1. 用 `scripts/find_workflow_library.py --json` 找到库根目录；必要时相对技能目录解析脚本路径。
   - 如有需要，先把 `AGENT_WORKFLOWS_ROOT` 设置为库根目录。
2. 读取库根目录下的 `README.md`。
3. 读取该工作流所需的最小共享文件集：
   - `shared/repository-preflight.md`
   - `shared/safety-rules.md`
   - `shared/workflow-conventions.md`
4. 读取选中的工作流文件。
5. 只有在工作流明确需要时，才继续打开其他章节或文件。

## 文件映射

- `project-initialization` -> `project-initialization-agent-workflow.md`
- `feature` -> `feature-development-agent-workflow.md`
- `bug-fix` -> `bug-fix-agent-workflow.md`
- `code-review` -> `code-review-agent-workflow.md`
- `incident` -> `incident-debugging-agent-workflow.md`
- `refactoring` -> `refactoring-agent-workflow.md`
- `tech-debt` -> `tech-debt-cleanup-agent-workflow.md`

## 默认共享文件

- 项目初始化：
读取对应工作流文件、安全规则、工作流约定，以及该工作流引用的目标仓库或上层工作区预检说明。

- 功能、缺陷修复、重构、技术债：
读取标准编码预检、匹配的安全规则和工作流约定。

- 代码评审：
读取代码评审预检、仅评审规则和工作流约定。

- 事故：
读取事故响应预检、事故响应规则和工作流约定。

## 加载纪律

- 不要因为文件存在就把所有工作流文件都加载进来。
- 同一时间只保留一个主工作流。
- 优先采用可移植的发现方式。不要把用户机器上的绝对路径硬编码到技能或工作流文档中。
- 如果需要交接，先完成建立交接依据的当前工作流步骤，再加载下一个工作流文件。
- 对重复样板内容，以共享文档为准；对任务专属步骤，以对应工作流文件为准。
