---
name: agent-coordinator
description: OpenClaw Agent 协调器 - 多 Agent 协作编排工具
emoji: 🌊
version: 1.0.0
author: Nova
---

## 概述

OpenClaw Agent Coordinator 是 OpenClaw 多 Agent 系统的协调编排工具，允许 主 Agent
自主调用和管理其他 Agent（DreamNova、Kiki、Coco、Iris、Luna 等），实现复杂的
多步骤任务协作。

## 功能

- **单 Agent 调用**: 调用指定 Agent 执行任务
- **工作流编排**: 定义多 Agent 协作流程
- **上下文传递**: 自动在 Agent 之间传递上下文
- **错误处理**: 失败重试、超时处理
- **结果聚合**: 汇总多 Agent 输出

## 使用方法

### 命令行

```bash
# 调用单个 Agent
claw skills run agent-coordinator --agent dreamnova --task "分析风险"

# 执行工作流
claw skills run agent-coordinator --workflow analyze_project   --steps "dreamnova:分析,kiki:优化,coco:生成报告"
```

### Python API

```python
from skills.agent_coordinator.coordinator import NovaAgentCoordinator

coordinator = NovaAgentCoordinator()

# 单 Agent 调用
result = coordinator.call_agent('dreamnova', '分析出海方案')

# 工作流
workflow = [
    {"agent": "dreamnova", "task": "分析风险", "use_context": False},
    {"agent": "kiki", "task": "优化方案", "use_context": True},
    {"agent": "coco", "task": "生成报告", "use_context": True}
]
result = coordinator.execute_workflow(workflow)
```

## 可用 Agents

| Agent | 角色 | 最佳用途 |
|-------|------|---------|
| dreamnova | 推演引擎 | 复杂决策、风险评估 |
| kiki | 优化专家 | 代码/方案优化 |
| coco | 执行者 | 文档生成、数据处理 |
| iris | 临床项目 | 临床试验、法规合规 |
| luna | 记忆管理 | 记忆检索、知识沉淀 |
| main | 主Agent | 基础对话 |

## 工作流示例

### 出海方案分析

```yaml
workflow:
  name: 出海方案分析
  steps:
    - agent: dreamnova
      task: 分析FDA申报风险
      timeout: 120
    
    - agent: iris
      task: 评估GCP合规要求
      use_context: true
    
    - agent: coco
      task: 生成执行计划
      use_context: true
```

## 配置

在 `~/.openclaw/skills/agent-coordinator/config.json`:

```json
{
  "default_timeout": 60,
  "max_retries": 2,
  "context_max_length": 2000,
  "preferred_agents": {
    "analysis": "dreamnova",
    "optimization": "kiki",
    "execution": "coco"
  }
}
```

## 依赖

- OpenClaw CLI >= 2026.2.26
- Python >= 3.9

## 版本历史

### v1.0.0 (2026-03-04)
- 初始版本
- 支持 7 个 Agent 调用
- 工作流编排功能
- 上下文传递机制
