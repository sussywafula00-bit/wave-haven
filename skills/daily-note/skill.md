# DailyNote - 每日笔记管理

## 描述
自动化的每日笔记系统，支持记录日常想法、任务追踪、会议摘要，并与多 Agent 系统集成。

## 功能
- 创建每日笔记（YYYY-MM-DD.md 格式）
- 记录灵感、想法、待办事项
- 从 wave-manager 拉取当日任务
- 每周自动生成回顾报告
- 支持标签系统 #tag
- 与 Luna 记忆系统集成

## 用法

### 命令行
```bash
# 创建今日笔记
claw skills run daily-note --today

# 添加笔记条目
claw skills run daily-note --add "会议讨论了架构方案 #work"

# 查看今日笔记
claw skills run daily-note --view

# 查看本周笔记
claw skills run daily-note --week

# 生成周回顾
claw skills run daily-note --review

# 搜索笔记
claw skills run daily-note --search "关键词"
```

### 自然语言（通过 Nova）
```
"Nova，记录日记：今天完成了 API 设计"
"查看今天的笔记"
"总结本周的关键决策"
"搜索关于架构的笔记"
```

## 配置
- 笔记存储路径：`~/.openclaw/shared/notes/daily/`
- 模板路径：`~/.openclaw/workspace/skills/daily-note/templates/`
- 归档路径：`~/.openclaw/shared/notes/archives/`

## 依赖
- wave-manager（拉取任务）
- memory-manager（Luna 集成）

## 作者
Nova 系统

## 版本
1.0.0
