# Knowledge Manager 存储结构修正说明

## 问题

错误地在 `~/.openclaw/workspace/agents/` 下创建存储，与主目录 `~/.openclaw/agents/` 重复，造成混乱。

## 正确的存储结构

```
~/.openclaw/                    # 主目录
├── agents/                     # ✅ Agent主目录（已存在）
│   ├── iris/
│   │   ├── workspace/
│   │   │   ├── SOUL.md
│   │   │   ├── knowledge_index.md  # ← Knowledge Manager索引存这里
│   │   │   └── ...
│   │   └── mid/temporal/       # ← TagMemo记忆存这里（已存在）
│   ├── nova/
│   ├── luna/
│   └── ...
│
├── workspace/                  # Workspace目录
│   ├── docs/                   # ✅ 共享文档库（知识管理使用）
│   │   ├── clinical/           # 临床相关
│   │   ├── regulatory/         # 法规相关
│   │   ├── technical/          # 技术相关
│   │   └── general/            # 通用知识
│   │
│   ├── skills/                 # 技能目录
│   │   └── knowledge-manager/  # Knowledge Manager技能
│   │
│   └── ...                     # 其他workspace内容
│
└── shared/                     # 共享数据
    └── notes/daily/            # DailyNote存储
```

## 修正方案

### 1. 代码路径修正

将 `~/.openclaw/workspace/agents/` 改为 `~/.openclaw/agents/`

### 2. 已存储数据的迁移

将 `~/.openclaw/workspace/agents/iris/` 下的内容合并到 `~/.openclaw/agents/iris/`

### 3. 文件权限

确保Knowledge Manager有权限写入 `~/.openclaw/agents/{agent}/`

## 为什么不放在workspace/agents/？

1. **职责分离**: workspace是开发/文档目录，agents是运行时数据
2. **已有结构**: `~/.openclaw/agents/` 已是标准的Agent主目录
3. **避免混淆**: 两个agents目录会让开发者和用户困惑
4. **一致性**: 其他系统（TagMemo）也使用 `~/.openclaw/agents/`
