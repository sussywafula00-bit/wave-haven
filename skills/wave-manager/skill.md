---
name: wave-manager
description: 浪潮任务管理系统 V3.0 - 增强版子任务状态流转 + 事件总线集成
emoji: 🌊
version: 3.0.0
---

## 概述

浪潮任务管理系统 V3.0 是 OpenClaw 多 Agent 协调引擎的核心组件，负责任务创建、分发、状态追踪和结果聚合。

### V3.0 新增特性
- **子任务状态流转**: created → assigned → in_progress → completed/failed
- **进度追踪**: 实时更新子任务进度 (0-100%)
- **事件总线集成**: 自动触发 DailyNote、知识沉淀
- **元数据增强**: 完整的执行时间线记录

## 核心概念

### 浪潮 (Wave)
浪潮是一个完整的任务单元，包含：
- 任务描述 (task)
- 子任务列表 (subtasks)
- 参与 Agent (agents)
- 执行日志 (logs)
- 元数据 (metadata)

### 子任务 (Subtask)
子任务的状态流转：
```
created → assigned → in_progress → completed
                              ↘ failed
```

每个子任务记录：
- 创建时间 (created_at)
- 分配时间 (assigned_at)
- 开始时间 (started_at)
- 完成时间 (completed_at)
- 执行进度 (progress: 0-100)
- 执行结果 (result)
- 错误信息 (error)
- 重试次数 (retry_count)

## Actions

### 基础操作

#### create - 创建新浪潮
```bash
python3 agent_v3.py '{"action": "create", "task": "任务描述"}'
```

#### assign - 分配子任务
```bash
python3 agent_v3.py '{
  "action": "assign",
  "wave_id": "Wave_xxx",
  "agent": "Luna",
  "subtask": "检索记忆"
}'
```

#### start - 开始执行子任务
```bash
python3 agent_v3.py '{
  "action": "start",
  "wave_id": "Wave_xxx",
  "subtask_id": "Wave_xxx_Luna_0"
}'
```

#### progress - 更新进度
```bash
python3 agent_v3.py '{
  "action": "progress",
  "wave_id": "Wave_xxx",
  "subtask_id": "Wave_xxx_Luna_0",
  "progress": 50,
  "message": "正在检索..."
}'
```

#### complete - 完成子任务
```bash
python3 agent_v3.py '{
  "action": "complete",
  "wave_id": "Wave_xxx",
  "subtask_id": "Wave_xxx_Luna_0",
  "result": {"found": "5条记忆"}
}'
```

#### fail - 标记失败
```bash
python3 agent_v3.py '{
  "action": "fail",
  "wave_id": "Wave_xxx",
  "subtask_id": "Wave_xxx_Luna_0",
  "error": "超时"
}'
```

#### status - 查询状态
```bash
python3 agent_v3.py '{
  "action": "status",
  "wave_id": "Wave_xxx"
}'
```

#### list - 列出浪潮
```bash
python3 agent_v3.py '{"action": "list"}'
python3 agent_v3.py '{"action": "list", "status": "completed"}'
```

### 版本管理

#### save_version - 保存版本
```bash
python3 agent_v3.py '{
  "action": "save_version",
  "version": "v1.2.0",
  "rules": {"routing": "new"}
}'
```

#### rollback - 回滚版本
```bash
python3 agent_v3.py '{
  "action": "rollback",
  "target_version": "v1.1.0"
}'
```

## 事件集成

Wave Manager V3.0 与事件总线深度集成，自动触发：

| 事件 | 触发时机 | 处理器 |
|------|----------|--------|
| WAVE_CREATED | 浪潮创建 | DailyNote记录 |
| SUBTASK_ASSIGNED | 子任务分配 | - |
| SUBTASK_STARTED | 子任务开始 | - |
| SUBTASK_PROGRESS | 进度更新 | - |
| SUBTASK_COMPLETED | 子任务完成 | DailyNote记录 |
| SUBTASK_FAILED | 子任务失败 | - |
| WAVE_COMPLETED | 浪潮完成 | 知识沉淀 |

## 数据存储

### 浪潮文件结构
```json
{
  "wave_id": "Wave_20260306_070859",
  "status": "completed",
  "task": "测试子任务状态流转",
  "creator": "Nova",
  "created_at": "2026-03-06T07:08:59...",
  "completed_at": "2026-03-06T07:09:00...",
  "agents": ["Luna"],
  "subtasks": [
    {
      "subtask_id": "Wave_20260306_070859_Luna_0",
      "agent": "Luna",
      "desc": "检索相关记忆",
      "status": "completed",
      "progress": 100,
      "created_at": "...",
      "assigned_at": "...",
      "started_at": "...",
      "completed_at": "...",
      "result": {"found": "5条记忆"},
      "error": null,
      "retry_count": 0
    }
  ],
  "logs": [],
  "metadata": {
    "total_subtasks": 1,
    "completed_subtasks": 1,
    "failed_subtasks": 0
  }
}
```

## 状态查询响应

```json
{
  "status": "success",
  "wave": { ... },
  "progress": 100.0,
  "summary": {
    "total": 1,
    "completed": 1,
    "in_progress": 0,
    "failed": 0,
    "pending": 0
  }
}
```

## 相关组件

- **wave-event-bus**: 事件总线
- **dream-orchestrator**: 梦境推演编排
- **wave-monitor**: 监控告警
- **knowledge-flow**: 知识流自动化

## 版本历史

### V3.0.0 (2026-03-06)
- 新增子任务状态流转 (5个状态)
- 新增进度追踪功能
- 集成事件总线
- 增强元数据记录
- 新增 `start`, `progress`, `fail` 操作

### V2.0.0
- 基础浪潮管理
- 子任务分配
- 状态查询
- 版本管理
