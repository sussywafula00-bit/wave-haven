# DailyNote V6.0 使用文档

## 概述

DailyNote V6.0 是自动记录增强版，提供标准化的自动触发点和统一的记录格式。

## 自动触发点

### 1. 任务相关

```bash
# 任务启动
python3 agent_v6.py task_start "任务名称" [wave_id]

# 任务完成
python3 agent_v6.py task_complete "任务名称" [wave_id]

# 通用记录（支持所有触发类型）
python3 agent_v6.py record "内容" task_start [wave_id]
```

### 2. 里程碑与决策

```bash
# 记录里程碑
python3 agent_v6.py milestone "达成XX里程碑" [wave_id]

# 记录决策
python3 agent_v6.py decision "采用XX方案" [wave_id]
```

### 3. 产出交付

```bash
python3 agent_v6.py output "交付XX功能" [wave_id]
```

## 记录格式

V6.0 采用标准化的条目格式：

```markdown
### 🚀 任务启动
**时间:** 14:30:00
**内容:** 启动任务: 基础设施优化
**关联浪潮:** `infra-opt-001`
**产出文件:** `agent_v6.py`, `agent_v2.py`
**决策摘要:** 采用向量索引方案
**标签:** `#开始` `#优化` `#架构`
**重要性:** ⭐⭐⭐
```

## 自动提取功能

### 1. 文件路径自动提取

内容中的文件路径会被自动提取：
- 代码块中的文件：`agent.py`
- Markdown 链接中的文件：[文件.md]
- 绝对路径：`/path/to/file.py`

### 2. 决策自动识别

包含 "决策:" 或 "决定:" 的内容会自动提取摘要。

### 3. 重要性自动计算

基于触发类型和内容关键词自动计算：
- 里程碑 (+0.4)
- 决策 (+0.35)
- 任务完成 (+0.3)
- 产出 (+0.25)
- 高优先级关键词 (+0.2)

## 笔记结构

V6.0 笔记包含以下章节：

```
📈 今日统计          # 自动更新
🎯 任务追踪          # 任务相关记录
🏆 里程碑            # 关键里程碑
🎯 决策记录          # 重要决策
📦 产出交付          # 产出物记录
💡 灵感与想法        # 灵感想法
📝 会议记录          # 会议内容
📚 学习记录          # 学习内容
📊 语义组分析        # 自动分析
```

## 集成使用

### 在 Wave 任务中自动记录

```python
# 任务开始时
subagent.run("daily-note", {
    "action": "task_start",
    "task": "API设计",
    "wave_id": "wave-001"
})

# 任务完成时
subagent.run("daily-note", {
    "action": "task_complete",
    "task": "API设计",
    "outputs": ["api.yaml", "design.md"],
    "wave_id": "wave-001"
})
```

## 版本对比

| 特性 | V5 | V6 |
|------|-----|-----|
| 自动触发 | 基础 | 9种标准化触发点 |
| 格式 | 自由 | 标准化条目 |
| WaveID | 手动 | 自动提取/传入 |
| 文件提取 | 无 | 自动提取 |
| 决策摘要 | 无 | 自动识别 |
| 重要性 | 固定 | 智能计算 |
