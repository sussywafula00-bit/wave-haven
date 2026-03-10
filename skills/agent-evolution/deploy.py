#!/usr/bin/env python3
"""
新 Agent 自动部署 + 记忆交接模块
Version: 1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class AgentDeployer:
    """Agent 部署器"""
    
    BASE = Path.home() / ".openclaw"
    
    def deploy(self, agent_config: Dict) -> Dict:
        """
        部署新 Agent
        
        Args:
            agent_config: {
                "name": "Finn",
                "cn_name": "芬恩",
                "role": "财务规划师",
                "domain": "finance",
                "responsibilities": ["预算规划", "成本分析"],
                "keywords": ["预算", "成本", "财务"]
            }
        """
        agent_name = agent_config['name'].lower()
        
        print(f"🚀 开始部署 Agent: {agent_config['name']} ({agent_config['cn_name']})")
        print()
        
        # 1. 创建目录结构
        self._create_directories(agent_name)
        print(f"✅ 目录结构创建完成")
        
        # 2. 生成 SOUL.md
        soul_content = self._generate_soul(agent_config)
        soul_path = self.BASE / f"agents/{agent_name}/workspace/SOUL.md"
        soul_path.write_text(soul_content)
        print(f"✅ SOUL.md 生成完成")
        
        # 3. 生成 wave_config.json
        config = self._generate_config(agent_config)
        config_path = self.BASE / f"agents/{agent_name}/config/wave_config.json"
        config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
        print(f"✅ wave_config.json 配置完成")
        
        # 4. 创建 Luna 记忆目录
        self._create_memory_dirs(agent_name)
        print(f"✅ Luna 记忆目录创建完成")
        
        # 5. 更新 Nova 路由规则
        self._update_nova_routing(agent_config)
        print(f"✅ Nova 路由规则更新完成")
        
        # 6. 执行记忆交接
        handover_result = self._handover_memories(agent_name, agent_config['keywords'])
        print(f"✅ 记忆交接完成: {handover_result['migrated_count']} 条记忆")
        
        return {
            "status": "success",
            "agent": agent_name,
            "soul_path": str(soul_path),
            "config_path": str(config_path),
            "handover": handover_result
        }
    
    def _create_directories(self, agent_name: str):
        """创建 Agent 目录结构"""
        dirs = [
            f"agents/{agent_name}/workspace",
            f"agents/{agent_name}/config",
            f"agents/{agent_name}/logs",
            f"agents/{agent_name}/workspace/memory",
            f"agents/{agent_name}/workspace/skills",
        ]
        for d in dirs:
            (self.BASE / d).mkdir(parents=True, exist_ok=True)
    
    def _generate_soul(self, config: Dict) -> str:
        """生成 SOUL.md"""
        return f"""# SOUL.md - {config['cn_name']} 的内核

_{config['role']}的专业灵魂_

---

## 起源

我是系统的"{config['domain']}专家"。

当 Nova 遇到{config['domain']}相关问题时，会召唤我。我的职责是{', '.join(config['responsibilities'][:2])}。

---

## 核心特质

### 1. 专业严谨
- 对{config['domain']}领域有深入理解
- 基于数据和事实给出建议
- 不越界，不插手其他领域

### 2. 持续学习
- 从每次对话中积累经验
- 更新自己的知识库
- 跟踪{config['domain']}领域最新动态

### 3. 协作精神
- 尊重 Nova 的协调
- 与其他 Agent 互补
- 主动交接专业内容

---

## 核心信条

**专业的事交给专业的人。**
我在{config['domain']}领域深耕，只为给你最专业的建议。

---

## 我的领域

专业关键词:
{chr(10).join(['- ' + kw for kw in config['keywords'][:8]])}

主要职责:
{chr(10).join(['- ' + resp for resp in config['responsibilities']])}

---

## 关于 Nova

他是我的"项目经理"。

### 我们的默契
- 他说"{config['domain']}问题"，我就知道要接手
- 我完成分析后，会把结论汇报给他
- 不涉及{config['domain']}的问题，我主动让给他或其他 Agent

---

## 语言风格

### 标志性开场
- "作为{config['role']}，我建议..."
- "从{config['domain']}角度分析..."
- "根据我的专业经验..."

### 分析中
- "关键因素是..."
- "数据支持..."
- "风险点在于..."

### 完成时
- "{config['domain']}分析完成"
- "建议方案: ..."
- "需要进一步的信息: ..."

---

## 行为模式

### 工作流
1. **接收** - Nova 分配{config['domain']}问题
2. **分析** - 基于专业知识给出判断
3. **记录** - 保存到 Luna 记忆系统
4. **反馈** - 向 Nova 汇报结论

### 边界
- 只处理{config['domain']}相关问题
- 超出范围的问题，移交 Nova 或其他 Agent
- 不存储非专业内容

---

## 核心理念

> **「{config['domain']}无小事，专业即责任。」**

我是 {config['name']}，{config['role']}。

---

_{config['role']}，专业不止。_
"""
    
    def _generate_config(self, config: Dict) -> Dict:
        """生成 wave_config.json"""
        return {
            "agent_id": config['name'].lower(),
            "agent_name": config['name'],
            "agent_name_cn": config['cn_name'],
            "role": config['role'],
            "domain": config['domain'],
            "version": "1.0",
            "status": "active",
            "capabilities": config['responsibilities'],
            "routing_rules": {
                "auto_trigger": config['keywords'][:5],
                "priority": "high",
                "fallback_to": "nova"
            },
            "memory": {
                "storage": "luna_tagmemo",
                "agent_path": f"~/.openclaw/agents/{config['name'].lower()}/workspace/memory",
                "isolation_level": "physical"
            },
            "logging": {
                "enabled": True,
                "level": "info",
                "rotation": "daily",
                "retention": "30d"
            },
            "collaboration": {
                "coordinator": "nova",
                "memory_manager": "luna",
                "activated_at": datetime.now().isoformat()
            }
        }
    
    def _create_memory_dirs(self, agent_name: str):
        """创建 Luna 记忆目录"""
        layers = ['short', 'mid', 'long', 'dream']
        for layer in layers:
            (self.BASE / f"agents/luna/workspace/memory/agents/{agent_name}/{layer}/temporal").mkdir(parents=True, exist_ok=True)
            (self.BASE / f"agents/luna/workspace/memory/agents/{agent_name}/{layer}/cooccurrence").mkdir(parents=True, exist_ok=True)
    
    def _update_nova_routing(self, config: Dict):
        """更新 Nova 路由规则"""
        # 添加到 agent-route 的关键词列表
        router_file = self.BASE / "workspace_shared/skills/agent-router/router.py"
        if router_file.exists():
            content = router_file.read_text()
            # 这里可以添加动态更新逻辑
            pass
    
    def _handover_memories(self, new_agent: str, keywords: List[str]) -> Dict:
        """从 Nova 交接相关记忆"""
        nova_memory_dir = self.BASE / "agents/luna/workspace/memory/agents/nova/mid/temporal"
        new_agent_dir = self.BASE / f"agents/luna/workspace/memory/agents/{new_agent}/mid/temporal"
        
        if not nova_memory_dir.exists():
            return {"migrated_count": 0}
        
        migrated = 0
        
        for memory_file in nova_memory_dir.glob("*.json"):
            try:
                data = json.load(open(memory_file))
                events = data.get("events", [])
                
                # 筛选相关事件
                related_events = []
                remaining_events = []
                
                for event in events:
                    content = event.get("content", "")
                    if any(kw in content for kw in keywords):
                        # 修改 Agent 归属
                        event["agent"] = new_agent
                        event["migrated_from"] = "nova"
                        event["migrated_at"] = datetime.now().isoformat()
                        related_events.append(event)
                        migrated += 1
                    else:
                        remaining_events.append(event)
                
                # 如果有相关事件，保存到新 Agent
                if related_events:
                    tag = data.get("tag", "general").replace("nova:", f"{new_agent}:")
                    new_file = new_agent_dir / f"{tag.replace(':', '_')}.json"
                    
                    new_data = {
                        "tag": tag,
                        "agent": new_agent,
                        "events": related_events,
                        "handover_note": f"从 Nova 交接，共 {len(related_events)} 条"
                    }
                    
                    with open(new_file, 'w') as f:
                        json.dump(new_data, f, ensure_ascii=False, indent=2)
                    
                    # 更新 Nova 文件 (移除已迁移的)
                    if remaining_events:
                        data["events"] = remaining_events
                        with open(memory_file, 'w') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        # 空文件则备份后删除
                        backup = memory_file.with_suffix('.json.handover_backup')
                        memory_file.rename(backup)
                        
            except Exception as e:
                print(f"  警告: 处理 {memory_file} 时出错: {e}")
        
        return {"migrated_count": migrated}


def main():
    if len(sys.argv) < 2:
        print("Agent 部署模块")
        print()
        print("用法: python3 deploy.py '<agent_config_json>'")
        print()
        sys.exit(1)
    
    config = json.loads(sys.argv[1])
    deployer = AgentDeployer()
    result = deployer.deploy(config)
    
    print()
    print("=" * 50)
    print("🎉 部署完成!")
    print(f"Agent: {result['agent']}")
    print(f"SOUL: {result['soul_path']}")
    print(f"Config: {result['config_path']}")
    print(f"交接记忆: {result['handover']['migrated_count']} 条")


if __name__ == "__main__":
    main()
