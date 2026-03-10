# Knowledge Manager

知识管理系统 - 统一的知识学习、存储、查询平台

## 功能

- **文档学习**: 解析文档，提取知识片段，存储到记忆系统
- **知识查询**: 支持轻量查询（TagMemo）和深度查询（完整文档）
- **智能索引**: 自动维护各Agent的知识索引
- **领域识别**: 自动判断知识属于哪个Agent的领域

## 支持的文档格式

| 格式 | 支持状态 | 说明 |
|------|----------|------|
| **Markdown (.md)** | ✅ 原生支持 | 推荐格式，结构清晰 |
| **文本 (.txt)** | ✅ 原生支持 | 纯文本，无需额外依赖 |
| **Word (.docx)** | ✅ 基础支持 | 解压XML提取文本 |
| **PDF (.pdf)** | ⚠️ 需安装依赖 | 安装pdfplumber或PyPDF2 |

## PDF支持说明

### 安装依赖（任选其一）

```bash
# 方法1: pdfplumber (推荐，中文支持好)
pip install pdfplumber

# 方法2: PyPDF2 (纯Python，无需额外依赖)
pip install PyPDF2

# 方法3: pdftotext (系统工具，Linux/Mac)
# Ubuntu/Debian: sudo apt-get install poppler-utils
# Mac: brew install poppler
```

### PDF学习示例

```bash
# 学习PDF文档
python agent.py learn ~/Documents/指南.pdf iris 临床

# 系统会自动尝试使用可用的PDF解析器
```

## 安装

无需额外安装，系统已集成到OpenClaw技能目录

**可选依赖（用于PDF支持）**:
```bash
pip install pdfplumber PyPDF2
```

## 使用方法

### 命令行使用

```bash
# 进入技能目录
cd ~/.openclaw/workspace/skills/knowledge-manager

# 学习文档（支持.md, .txt, .docx, .pdf）
python agent.py learn ~/Documents/出海手册.md iris 出海,临床
python agent.py learn ~/Documents/指南.pdf iris 临床

# 查询知识
python agent.py query 'CtQ是什么' iris light

# 查看知识摘要
python agent.py summary iris
```

## 最佳实践

### 文档格式选择

1. **优先使用Markdown** (.md)
   - 结构清晰，易于解析
   - 支持标题层级，利于知识切片
   - 无需额外依赖

2. **次选纯文本** (.txt)
   - 简单直接
   - 适合快速记录

3. **Word文档** (.docx)
   - 基础支持，可能丢失格式
   - 复杂表格可能解析不完整

4. **PDF文档** (.pdf)
   - 需要安装pdfplumber或PyPDF2
   - 扫描版PDF无法解析（需要OCR）
   - 复杂排版可能解析不完整

## 存储结构

```
~/.openclaw/agents/{agent}/
├── workspace/
│   └── knowledge_index.md    # 知识索引
└── mid/temporal/             # TagMemo记忆
    └── km_*.json

~/.openclaw/workspace/docs/
└── clinical/                 # 原始文档（支持所有格式）
    ├── 出海手册.md
    ├── 指南.pdf
    └── 规范.docx
```

## 集成

### 与WaveRouter集成

WaveRouter识别"学习"、"查询"意图，路由到Knowledge Manager

### 与DailyNote集成

学习行为自动记录到DailyNote

## 版本

v1.1.0 - 增强PDF支持
- 文档学习功能
- 知识查询功能
- 智能领域识别
- 分层查询策略
- ✅ PDF支持（需安装依赖）

v1.0.0 - 初始版本
- 基础文档学习
- 知识查询功能
- 智能领域识别
