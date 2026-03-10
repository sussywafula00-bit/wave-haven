# Knowledge Manager 系统技术实施文档

## 版本信息

- **文档版本**: v1.0
- **创建日期**: 2026-03-04
- **系统版本**: Knowledge Manager v1.0.0
- **关联版本**: WaveRouter V5.0, DailyNote V5.0

## 系统概述

Knowledge Manager 是一个独立的知识管理系统，负责：
1. 文档学习（解析、提取、存储）
2. 知识查询（轻量/深度查询）
3. 智能索引（自动维护知识索引）
4. 领域识别（自动判断Agent归属）

## 文件清单

```
skills/knowledge-manager/
├── agent.py              # 主入口（主程序）
├── skill.md              # 技能说明文档
├── core/
│   ├── learner.py        # 文档学习引擎（核心）
│   └── querier.py        # 知识查询引擎（核心）
└── utils/                # 工具函数（预留）

skills/wave-router/
├── router_v5.py          # 浪潮路由器V5（知识意图识别）

skills/daily-note/
└── agent_v5.py           # 日记管理V5（学习事件通知）
```

## 系统架构

```
┌─────────────────────────────────────────────────────┐
│                    用户输入层                        │
│  "学习出海手册" / "CtQ是什么？" / 上传文档            │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                 WaveRouter V5                        │
│  - 意图识别（新增知识意图检测）                       │
│  - 路由决策：知识相关 → Knowledge Manager            │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│              Knowledge Manager                       │
│  ├─ learner.py:  文档解析 → 知识提取 → 存储        │
│  ├─ querier.py:  知识查询（light/deep）             │
│  └─ agent.py:    统一入口                          │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│                  存储层                              │
│  ├─ docs/clinical/          原始文档               │
│  ├─ agents/{agent}/mid/     TagMemo记忆            │
│  └─ agents/{agent}/workspace/knowledge_index.md   │
└───────────────────────┬─────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│               DailyNote V5                           │
│  - 学习记录自动同步                                  │
│  - 事件通知Knowledge Manager                         │
└─────────────────────────────────────────────────────┘
```

## 核心模块详解

### 1. DocumentLearner (learner.py)

**功能**: 将文档转化为结构化知识

**主要方法**:
- `ingest(file_path, context)`: 学习文档入口
- `_parse_document(path)`: 解析不同格式文档
  - `.md`, `.txt`: 原生支持
  - `.docx`: 解压XML提取文本
  - `.pdf`: 需安装pdfplumber/PyPDF2
- `_detect_agent_domain(content)`: 自动判断Agent领域
- `_extract_knowledge_chunks(content)`: 提取知识片段
- `_save_to_tagmemo(agent, chunk)`: 保存到TagMemo

**PDF解析方案**:
```python
# 优先级顺序:
1. pdfplumber (推荐，中文支持好)
2. PyPDF2 (纯Python)
3. pdftotext (系统命令)
4. Fallback (提示安装依赖)
```

**使用示例**:
```python
from core.learner import DocumentLearner

learner = DocumentLearner()

# 学习Markdown
result = learner.ingest("/path/to/doc.md", {
    "source": "user_upload",
    "tags": ["出海", "临床"]
})

# 学习PDF（需安装依赖）
result = learner.ingest("/path/to/doc.pdf", {
    "source": "user_upload",
    "tags": ["法规", "指南"]
})
```

### 2. KnowledgeQuerier (querier.py)

**功能**: 按需查询知识

**主要方法**:
- `query(question, agent, depth)`: 查询入口
- `_light_query()`: 轻量查询（TagMemo）
- `_deep_query()`: 深度查询（完整文档）
- `_decide_depth()`: 自动判断查询深度

**查询深度策略**:
- **light**: 简单定义问题、有明确关键词
- **deep**: 流程/对比/复杂问题
- **auto**: 自动判断（默认）

**使用示例**:
```python
from core.querier import KnowledgeQuerier

querier = KnowledgeQuerier()
result = querier.query("CtQ是什么？", agent="iris", depth="light")
```

### 3. WaveRouter V5 (router_v5.py)

**新增功能**: 知识意图识别

**检测逻辑**:
```python
# 学习意图关键词
["学习", "笔记", "总结", "上传", "添加知识", "保存文档"]

# 查询意图关键词  
["什么是", "告诉我", "查找", "搜索知识", "查询", "了解"]

# 路由决策
if is_knowledge_intent:
    if type == "learn":
        route_to = "KnowledgeManager"
        action = "知识学习"
    else:
        route_to = "KnowledgeManager"
        action = "知识查询"
```

### 4. DailyNote V5 (agent_v5.py)

**新增功能**: 学习事件自动通知

**检测逻辑**:
```python
learning_keywords = ["学习", "笔记", "总结", "阅读", "研究", "探索"]

if _is_learning_content(content):
    category = "learning"
    _notify_knowledge_manager(content, tags)
```

## 存储结构

### 原始文档
```
~/.openclaw/workspace/docs/           # ✅ Workspace下的共享文档库
├── clinical/                         # 临床相关（iris）
│   └── 出海手册_20260304.md
├── regulatory/                       # 法规相关
├── technical/                        # 技术相关（kiki）
└── general/                          # 通用知识
```

### TagMemo记忆
```
~/.openclaw/agents/{agent}/           # ✅ 主目录下的Agent专属记忆
└── mid/temporal/
    └── km_20260304_001.json          # Knowledge Manager生成的记忆
```

### 知识索引
```
~/.openclaw/agents/{agent}/           # ✅ 主目录下的知识索引
└── workspace/
    └── knowledge_index.md
```

## 使用指南

### 命令行使用

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/knowledge-manager

# 学习文档
python agent.py learn ~/Documents/出海手册.md iris 出海,临床

# 查询知识
python agent.py query 'CtQ是什么' iris light

# 查看知识摘要
python agent.py summary iris
```

### 集成使用（通过WaveRouter）

```bash
# WaveRouter自动识别知识意图
cd ~/.openclaw/workspace/skills/wave-router
python router_v5.py '学习出海手册'
# 输出: 路由到 KnowledgeManager | 动作: 知识学习

python router_v5.py 'CtQ是什么'
# 输出: 路由到 KnowledgeManager | 动作: 知识查询
```

### 通过DailyNote记录学习

```bash
cd ~/.openclaw/workspace/skills/daily-note
python agent_v5.py add '学习了ICH E6(R3)的CtQ框架' learning
# 自动检测为学习内容，通知Knowledge Manager
```

## 测试方案

### 测试1：文档学习流程

```bash
# 1. 准备测试文档
echo "# 测试文档
## CtQ定义
CtQ是关键质量因素...

## QTLs定义
QTL是质量容忍限..." > /tmp/test_doc.md

# 2. 执行学习
cd ~/.openclaw/workspace/skills/knowledge-manager
python agent.py learn /tmp/test_doc.md iris 测试

# 3. 验证存储
ls ~/.openclaw/workspace/docs/clinical/
ls ~/.openclaw/workspace/agents/iris/mid/temporal/
cat ~/.openclaw/workspace/agents/iris/workspace/knowledge_index.md
```

**预期结果**:
- 文档保存到 `docs/clinical/`
- 知识片段保存到 `agents/iris/mid/temporal/`
- 索引更新到 `knowledge_index.md`

### 测试2：知识查询流程

```bash
# 执行查询
python agent.py query 'CtQ是什么' iris light

# 预期输出
{
  "status": "success",
  "agent": "iris",
  "answer": "CtQ是关键质量因素...",
  "source": "tagmemo",
  "confidence": 0.85
}
```

### 测试3：WaveRouter集成

```bash
cd ~/.openclaw/workspace/skills/wave-router
python router_v5.py '学习出海手册'

# 预期输出
{
  "action": "知识学习",
  "target": "KnowledgeManager",
  "type": "knowledge",
  "message": "📚 检测到知识学习意图..."
}
```

### 测试4：DailyNote集成

```bash
cd ~/.openclaw/workspace/skills/daily-note
python agent_v5.py add '学习了出海项目的质量管理' thoughts

# 预期输出
{
  "status": "success",
  "category": "learning",
  "is_learning": true,
  "knowledge_notification": {
    "status": "notified",
    ...
  }
}
```

## 升级回滚方案

### 如果V5有问题，回滚到V4

```bash
# WaveRouter回滚
cd ~/.openclaw/workspace/skills/wave-router
ln -sf router_v4.py router.py

# DailyNote回滚
cd ~/.openclaw/workspace/skills/daily-note
ln -sf agent_v4.py agent.py
```

### Knowledge Manager是新增系统，不影响原有功能

## 性能指标

| 操作 | 预期时间 | 说明 |
|------|---------|------|
| 文档学习 | 2-5秒 | 取决于文档大小 |
| 轻量查询 | <1秒 | 查TagMemo |
| 深度查询 | 3-10秒 | 读取完整文档 |
| 意图识别 | <0.1秒 | WaveRouter |

## 故障排查

### 问题1：文档学习失败

**症状**: `ingest()`返回错误

**排查**:
1. 检查文件路径是否存在
2. 检查文件格式是否支持（.md, .txt, .docx）
3. 检查目录权限

### 问题2：查询无结果

**症状**: `query()`返回空结果

**排查**:
1. 检查是否有知识存储：`python agent.py summary`
2. 检查TagMemo目录是否存在
3. 尝试深度查询：`depth="deep"`

### 问题3：WaveRouter未识别知识意图

**症状**: 知识相关输入被路由到其他Agent

**排查**:
1. 检查`is_knowledge_intent()`检测逻辑
2. 测试关键词是否在列表中
3. 查看路由输出JSON

## 后续优化方向

1. **NLP增强**: 使用真正的NLP库提取关键词
2. **向量搜索**: 使用Embedding进行语义搜索
3. **多语言支持**: 支持英文文档学习
4. **PDF解析**: 完善PDF文档解析
5. **知识图谱**: 构建Agent间的知识关系图

## 附录

### A. 文件权限检查

```bash
# 检查目录权限
ls -la ~/.openclaw/workspace/docs/
ls -la ~/.openclaw/workspace/agents/iris/mid/

# 修复权限
chmod -R 755 ~/.openclaw/workspace/docs/
chmod -R 755 ~/.openclaw/workspace/agents/
```

### B. 依赖检查

Knowledge Manager纯Python实现，依赖：
- Python 3.8+
- 标准库：json, re, pathlib, datetime
- 可选：python-docx（完整DOCX支持）

### C. 调试模式

```python
# 在代码中添加调试输出
import logging
logging.basicConfig(level=logging.DEBUG)

# 或者在主程序中
if __name__ == "__main__":
    import sys
    # 添加-v参数启用详细输出
    if "-v" in sys.argv:
        print("详细模式启用...")
```

---

**文档结束**

**维护记录**:
- 2026-03-04: 初始版本 v1.0
