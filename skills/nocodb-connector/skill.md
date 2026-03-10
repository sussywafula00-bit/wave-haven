---
name: nocodb-connector
description: Connect to NocoDB and sync data for agent learning. Supports full table export, incremental sync, and automatic knowledge indexing.
homepage: https://nocodb.com
metadata: {"clawdbot":{"emoji":"🗄️","requires":{"bins":["python3","pip"],"env":["NOCODB_URL"]},"primaryEnv":"NOCODB_URL"}}
---

# NocoDB Connector

连接 NocoDB 数据库，为 Agent 提供数据同步和知识学习功能。

## 功能

- **全表导出**: 导出 NocoDB 表的全部数据
- **增量同步**: 基于时间戳的增量数据同步
- **自动学习**: 导出后自动触发 Knowledge Manager 学习
- **多表支持**: 支持多个 NocoDB 表连接

## 安装依赖

```bash
pip install requests pandas
```

## 使用方法

### 1. 配置 NocoDB 连接

设置环境变量或配置文件：

```bash
# 方式1: 环境变量
export NOCODB_URL="http://localhost:8080"
export NOCODB_TOKEN="your_api_token"  # 如果需要认证

# 方式2: 配置文件
~/.openclaw/config/nocodb.json
```

### 2. 导出数据

```bash
# 导出整个表
cd ~/.openclaw/workspace/skills/nocodb-connector
python agent.py export \
  --base p658guol32wpk14 \
  --table master_risk_staging \
  --agent iris \
  --output ~/.openclaw/workspace/docs/clinical/

# 增量同步（基于 updated_at 字段）
python agent.py sync \
  --base p658guol32wpk14 \
  --table master_risk_staging \
  --since 2026-03-04 \
  --agent iris
```

### 3. 自动学习

导出后自动触发 Knowledge Manager 学习：

```bash
python agent.py export-and-learn \
  --base p658guol32wpk14 \
  --table master_risk_staging \
  --agent iris
```

## 参数说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `--base` | NocoDB Base ID | p658guol32wpk14 |
| `--table` | 表名 | master_risk_staging |
| `--agent` | 学习目标 Agent | iris |
| `--output` | 输出目录 | ~/.openclaw/workspace/docs/clinical/ |
| `--format` | 输出格式 | markdown, json, csv |
| `--since` | 增量同步起始时间 | 2026-03-04 |

## 输出格式

### Markdown（推荐）
- 结构清晰，适合 Knowledge Manager 学习
- 自动添加元数据头部

### JSON
- 完整数据结构保留
- 适合程序化处理

### CSV
- 通用格式
- 适合 Excel 查看

## 集成

### 与 Knowledge Manager 集成

导出后自动调用 Knowledge Manager 进行学习：

```python
# 自动学习流程
1. 从 NocoDB 导出数据
2. 格式化为 Markdown
3. 调用 knowledge-manager/agent.py learn
4. 更新 Agent 的 knowledge_index.md
5. 重新生成 TagMemo 共现矩阵
```

### 与 DailyNote 集成

同步记录自动写入 DailyNote：

```
[2026-03-05] NocoDB 同步: master_risk_staging
- 新增记录: 2,500 条
- 更新记录: 150 条
- 学习状态: 成功
```

## 存储结构

```
~/.openclaw/
├── workspace/docs/clinical/
│   └── {table}_full_YYYYMMDD.md      # 全量导出
│   └── {table}_incremental_YYYYMMDD.md  # 增量导出
├── agents/{agent}/
│   └── workspace/knowledge_index.md  # 知识索引
│   └── mid/temporal/                 # TagMemo 数据
└── config/nocodb.json                # 连接配置
```

## 版本

v1.0.0 - 初始版本
- NocoDB API 连接
- 全表导出功能
- Markdown/JSON/CSV 格式支持
- 自动 Knowledge Manager 学习

## 故障排除

### 连接失败

检查 NocoDB 服务是否运行：
```bash
curl http://localhost:8080/api/v1/health
```

### 认证失败

如果 NocoDB 启用了认证，设置 API Token：
```bash
export NOCODB_TOKEN="your_token_here"
```

### 数据量大导致超时

使用分页导出：
```bash
python agent.py export \
  --base p658guol32wpk14 \
  --table master_risk_staging \
  --batch-size 1000 \
  --agent iris
```
