# Agent Coordinator Skill

Nova 浪潮协调器 - 多 Agent 协作编排工具

## 快速开始

```bash
# 调用单个 Agent
python3 agent.py --agent dreamnova --task "分析风险" --json

# 执行工作流
python3 agent.py --workflow my_flow \
  --steps "dreamnova:分析,kiki:优化,coco:报告" \
  --json
```

## 可用 Agents

- **dreamnova**: 推演引擎，复杂决策分析
- **kiki**: 优化专家，代码/方案优化
- **coco**: 执行者，文档生成
- **iris**: 临床项目，试验管理
- **luna**: 记忆管理
- **nova**: 浪潮指挥官（协调者自身）
- **main**: 主Agent

## 文档

- `SKILL.md`: 技能定义文档
- `coordinator.py`: 协调器核心代码
- `agent.py`: 命令行入口
- `config.json`: 配置文件
