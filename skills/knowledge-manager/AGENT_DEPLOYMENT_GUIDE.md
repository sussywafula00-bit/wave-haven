# Knowledge Manager Agent部署指南

## 核心问题：是否所有Agent都需要部署知识系统？

**答案：否，不是所有Agent都需要部署。**

Knowledge Manager是**可选功能**，应根据各Agent的职责和需求决定是否部署。

---

## 部署策略矩阵

| Agent | 推荐部署 | 优先级 | 原因 | 建议类别 |
|-------|----------|--------|------|----------|
| **iris** | ✅ 强烈推荐 | 🔴 High | 临床运营专家，管理出海、GCP、法规等大量专业知识 | clinical, regulatory, 出海 |
| **dreamnova** | ✅ 推荐 | 🟡 Medium | 推演分析专家，可存储推演框架、分析方法 | analysis, framework, methodology |
| **kiki** | ✅ 推荐 | 🟡 Medium | 技术优化专家，可存储代码规范、架构模式 | technical, coding, architecture |
| **luna** | ⚪ 可选 | 🟢 Low | 记忆管理专家，本身管理TagMemo系统，可辅助但不必须 | memory, organization |
| **nova** | ❌ 不推荐 | 🟢 Low | 系统协调者，主要职责是路由协调，知识需求极少 | system, coordination |

---

## 部署原则

### 1. 按需部署原则

**需要部署的情况：**
- Agent管理大量领域专业知识
- 需要频繁查询和引用文档
- 有持续学习的专业内容

**不需要部署的情况：**
- Agent职责是协调/路由（如Nova）
- Agent本身已是记忆管理系统（如Luna）
- 无特定领域知识需要管理

### 2. 渐进式部署

```
Phase 1: 核心Agent (iris)
  └─ 临床知识、出海文档、法规指南

Phase 2: 专业Agent (dreamnova, kiki)  
  ├─ dreamnova: 分析框架、决策模型
  └─ kiki: 代码规范、技术文档

Phase 3: 可选Agent (luna, nova)
  └─ 根据实际需求决定
```

### 3. 物理隔离原则

每个Agent的知识**完全独立**：
- 不共享记忆（避免污染）
- 独立索引（各自管理）
- 独立存储（各自目录）

---

## 快速部署

### 查看当前状态

```bash
cd ~/.openclaw/workspace/skills/knowledge-manager
python deploy.py status
```

### 查看部署建议

```bash
python deploy.py recommend
```

### 为特定Agent部署

```bash
# 为iris部署（临床知识）
python deploy.py deploy iris clinical,regulatory,出海

# 为dreamnova部署（分析框架）
python deploy.py deploy dreamnova analysis,framework

# 为kiki部署（技术知识）
python deploy.py deploy kiki technical,coding
```

### 查看部署后的状态

```bash
python deploy.py status iris
```

---

## 各Agent部署详解

### iris（临床运营专家）- 强烈推荐部署

**为什么需要：**
- 管理出海项目质量管理手册（37KB专业文档）
- 需要频繁查询ICH E6(R3)、FDA法规
- 需要回答CtQ、QTLs等专业问题
- 存量项目出海需要参考历史知识

**建议类别：**
- `clinical`: 临床试验相关知识
- `regulatory`: 法规合规知识
- `出海`: 国际化相关知识
- `GCP`: 临床试验质量管理规范

**部署命令：**
```bash
python deploy.py deploy iris clinical,regulatory,出海,GCP
```

---

### dreamnova（推演分析专家）- 推荐部署

**为什么需要：**
- 存储推演分析框架和方法论
- 管理决策模型和评估标准
- 积累历史推演案例和经验
- 支持多方案对比分析

**建议类别：**
- `analysis`: 分析方法
- `framework`: 分析框架
- `methodology`: 方法论
- `decision`: 决策模型

**部署命令：**
```bash
python deploy.py deploy dreamnova analysis,framework,methodology
```

---

### kiki（技术优化专家）- 推荐部署

**为什么需要：**
- 存储代码规范和最佳实践
- 管理架构设计模式
- 积累技术债务识别方法
- 支持代码重构知识

**建议类别：**
- `technical`: 技术通用知识
- `coding`: 编码规范
- `architecture`: 架构设计
- `performance`: 性能优化

**部署命令：**
```bash
python deploy.py deploy kiki technical,coding,architecture
```

---

### luna（记忆管理专家）- 可选部署

**为什么不必须：**
- Luna本身已是记忆管理系统（TagMemo）
- 主要职责是记忆存储和检索
- 知识管理对其来说是重复功能

**何时需要：**
- 如果Luna需要管理记忆系统本身的操作手册
- 如果Luna需要学习记忆优化方法

**部署命令（可选）：**
```bash
python deploy.py deploy luna memory,organization
```

---

### nova（系统协调者）- 不推荐部署

**为什么不需要：**
- Nova主要职责是路由协调（WaveRouter）
- 不管理特定领域知识
- 知识需求极少（系统配置等可硬编码）

**替代方案：**
- 系统配置放在代码中
- 路由规则放在配置文件
- 不通过Knowledge Manager管理

---

## 部署后使用

### 1. 学习文档（以iris为例）

```bash
# 学习出海手册
python agent.py learn ~/Documents/出海手册.md iris 出海,临床

# 自动存储到：
# - docs/clinical/出海手册.md（原始文档）
# - agents/iris/mid/temporal/（TagMemo记忆）
# - agents/iris/workspace/knowledge_index.md（索引）
```

### 2. 查询知识

```bash
# iris查询CtQ定义
python agent.py query 'CtQ是什么' iris light

# dreamnova查询分析方法
python agent.py query 'SWOT分析怎么做' dreamnova light

# kiki查询代码规范
python agent.py query 'Python命名规范' kiki light
```

### 3. WaveRouter自动路由

```bash
# 自动识别为iris知识查询
python router.py '出海项目中如何设置CtQ'

# 自动识别为dreamnova知识查询  
python router.py '推演分析的步骤是什么'
```

---

## 权限和隔离

### 跨Agent查询限制

Knowledge Manager默认**不支持**跨Agent查询：
- iris的知识只能在iris域内查询
- 不能从kiki查询iris的临床知识
- 保持物理隔离，避免记忆污染

### 如果需要跨Agent共享

通过共享文档库实现：
```
~/.openclaw/workspace/docs/
├── clinical/      # iris管理
├── technical/     # kiki管理  
└── shared/        # 共享知识（只读）
```

---

## 成本考量

### Token消耗

| 操作 | Token消耗 | 适用场景 |
|------|-----------|----------|
| 轻量查询 | ~500 | 简单定义、常见问题 |
| 深度查询 | ~2000 | 复杂流程、详细解答 |
| 文档学习 | ~1000-5000 | 取决于文档大小 |

### 存储成本

- 原始文档：存储在本地，无额外成本
- TagMemo记忆：存储在本地，无额外成本
- 索引文件：纯文本，极小

**建议：**
- 只为高频使用的Agent部署
- 避免存储大量不常用知识
- 定期清理过时知识

---

## 总结

### 推荐部署的Agent

1. **iris** - 必须部署（临床知识核心）
2. **dreamnova** - 推荐部署（分析知识）
3. **kiki** - 推荐部署（技术知识）

### 可选部署的Agent

4. **luna** - 可选（如需要管理记忆系统知识）

### 不推荐部署的Agent

5. **nova** - 不需要（协调者无特定领域知识）

---

## 下一步操作

1. **查看当前状态**
   ```bash
   python deploy.py status
   ```

2. **查看部署建议**
   ```bash
   python deploy.py recommend
   ```

3. **为核心Agent部署**
   ```bash
   python deploy.py deploy iris clinical,regulatory,出海
   python deploy.py deploy dreamnova analysis,framework
   python deploy.py deploy kiki technical,coding
   ```

4. **验证部署**
   ```bash
   python deploy.py status
   ```

---

**核心原则：按需部署，避免过度设计。** 🎯
