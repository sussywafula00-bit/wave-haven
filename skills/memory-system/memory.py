#!/usr/bin/env python3
"""
记忆系统统一接口 v2.0
支持多Agent记忆写入 + 自动四层迁移
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

class UnifiedMemory:
    """统一记忆管理器"""
    
    AGENTS = ['nova', 'luna', 'kiki', 'coco', 'dreamnova', 'iris']
    LAYERS = ['short', 'mid', 'long', 'dream']
    
    # 各层保留时间（天）
    LAYER_RETENTION = {
        'short': 7,    # 7天
        'mid': 30,     # 30天
        'long': 90,    # 90天
        'dream': 365   # 1年
    }
    
    # Agent 专业领域关键词（用于自动路由）
    AGENT_DOMAINS = {
        'nova': ['系统', '协调', '管理', '任务', 'Wave', 'Haven'],
        'luna': ['记忆', '知识', '搜索', '归档', '整理'],
        'kiki': ['优化', '代码', '重构', '性能', '版本', '算法'],
        'coco': ['执行', '脚本', '部署', '运行', '生成', '完成'],
        'dreamnova': ['推演', '探索', '创新', '研究', '预测', '实验'],
        'iris': ['临床试验', 'GCP', '伦理', '患者', 'TQC', 'COPD', '哮喘']
    }
    
    def __init__(self):
        self.base = Path.home() / ".openclaw/agents/luna/workspace/memory/agents"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保目录结构存在"""
        for agent in self.AGENTS:
            for layer in self.LAYERS:
                (self.base / agent / layer / "temporal").mkdir(parents=True, exist_ok=True)
                (self.base / agent / layer / "cooccurrence").mkdir(parents=True, exist_ok=True)
    
    def _get_target_agent(self, content: str, suggested_agent: str = None) -> str:
        """根据内容自动判断应该写入哪个 Agent"""
        if suggested_agent and suggested_agent in self.AGENTS:
            # 验证内容是否符合该 Agent 的专业领域
            domain_keywords = self.AGENT_DOMAINS.get(suggested_agent, [])
            if any(kw in content for kw in domain_keywords):
                return suggested_agent
        
        # 自动匹配
        content_lower = content.lower()
        scores = {}
        for agent, keywords in self.AGENT_DOMAINS.items():
            score = sum(1 for kw in keywords if kw.lower() in content_lower)
            if score > 0:
                scores[agent] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return suggested_agent or 'nova'  # 默认 Nova
    
    def _get_target_layer(self, timestamp: datetime = None, importance: float = 0.5) -> str:
        """根据时间和重要性判断应该写入哪一层"""
        if timestamp is None:
            timestamp = datetime.now()
        
        age_days = (datetime.now() - timestamp).days
        
        # 根据时间和重要性综合判断
        if age_days <= 7 and importance >= 0.7:
            return 'short'  # 新的重要记忆
        elif age_days <= 30 or importance >= 0.5:
            return 'mid'    # 中期记忆
        elif age_days <= 90:
            return 'long'   # 长期记忆
        else:
            return 'dream'  # 深层记忆
    
    def write(self, 
              content: str, 
              agent: str = None,
              tags: List[str] = None,
              source: str = "system",
              importance: float = 0.5,
              layer: str = None) -> Dict[str, Any]:
        """
        统一写入接口
        
        Args:
            content: 记忆内容
            agent: 指定 Agent (None则自动判断)
            tags: 标签列表
            source: 来源
            importance: 重要性 (0-1)
            layer: 指定层级 (None则自动判断)
        
        Returns:
            写入结果信息
        """
        # 确定目标 Agent
        target_agent = self._get_target_agent(content, agent)
        
        # 确定目标层级
        target_layer = layer or self._get_target_layer(importance=importance)
        
        # 构建记忆数据
        now = datetime.now()
        memory_data = {
            "content": content,
            "agent": target_agent,
            "source": source,
            "tags": tags or [f"{target_agent}:general"],
            "importance": importance,
            "ts": now.isoformat(),
            "year": now.year,
            "month": now.month,
            "week": now.isocalendar()[1],
            "day_of_week": now.weekday(),
            "hour": now.hour
        }
        
        # 确定存储文件
        tag = tags[0] if tags else f"{target_agent}:general"
        safe_tag = tag.replace(':', '_').replace('/', '_')
        
        memory_file = self.base / target_agent / target_layer / "temporal" / f"{safe_tag}.json"
        
        # 读取或创建
        data = {"tag": tag, "agent": target_agent, "events": []}
        if memory_file.exists():
            with open(memory_file) as f:
                data = json.load(f)
        
        # 添加事件
        data["events"].append(memory_data)
        
        # 限制每个文件最多100条（防止过大）
        if len(data["events"]) > 100:
            data["events"] = data["events"][-100:]
        
        # 保存
        with open(memory_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 更新共现矩阵
        self._update_cooccurrence(target_agent, target_layer, tags or [tag])
        
        return {
            "status": "success",
            "agent": target_agent,
            "layer": target_layer,
            "file": str(memory_file),
            "total_events": len(data["events"])
        }
    
    def _update_cooccurrence(self, agent: str, layer: str, tags: List[str]):
        """更新共现矩阵"""
        matrix_file = self.base / agent / layer / "cooccurrence" / "matrix.json"
        
        data = {
            "version": "4.0",
            "type": "agent",
            "agent": agent,
            "layer": layer,
            "tags": {},
            "pairs": {}
        }
        
        if matrix_file.exists():
            with open(matrix_file) as f:
                data = json.load(f)
        
        now = datetime.now().isoformat()
        
        # 更新 Tag 计数
        for tag in tags:
            if tag not in data["tags"]:
                data["tags"][tag] = {
                    "count": 0,
                    "first_seen": now,
                    "last_seen": now
                }
            data["tags"][tag]["count"] += 1
            data["tags"][tag]["last_seen"] = now
        
        # 更新 Tag 对共现
        for i, tag1 in enumerate(tags):
            for tag2 in tags[i+1:]:
                pair_key = f"{tag1}||{tag2}"
                if pair_key not in data["pairs"]:
                    data["pairs"][pair_key] = 0
                data["pairs"][pair_key] += 1
        
        with open(matrix_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def migrate_layers(self, agent: str = None):
        """
        执行四层记忆迁移
        将过期记忆从高层级迁移到低层级
        """
        agents_to_migrate = [agent] if agent else self.AGENTS
        
        migrated_count = 0
        
        for ag in agents_to_migrate:
            # short (7天) → 删除
            short_dir = self.base / ag / "short" / "temporal"
            if short_dir.exists():
                for f in short_dir.glob("*.json"):
                    try:
                        data = json.load(open(f))
                        events = data.get("events", [])
                        
                        # 分离新旧事件
                        now = datetime.now()
                        new_events = []
                        old_events = []
                        
                        for event in events:
                            ts = datetime.fromisoformat(event.get("ts", now.isoformat()))
                            age_days = (now - ts).days
                            
                            if age_days <= self.LAYER_RETENTION['short']:
                                new_events.append(event)
                            else:
                                old_events.append(event)
                        
                        # 保存新事件
                        if new_events:
                            data["events"] = new_events
                            with open(f, 'w') as fp:
                                json.dump(data, fp, ensure_ascii=False, indent=2)
                        else:
                            # 删除空文件
                            f.unlink()
                        
                        # 迁移旧事件到 mid
                        if old_events:
                            for event in old_events:
                                self._migrate_event(ag, event, 'short', 'mid')
                            migrated_count += len(old_events)
                    except Exception as e:
                        print(f"Error migrating {f}: {e}")
            
            # mid (30天) → long
            # long (90天) → dream
            # 类似逻辑...
        
        return migrated_count
    
    def _migrate_event(self, agent: str, event: dict, from_layer: str, to_layer: str):
        """迁移单个事件"""
        tag = event.get("tags", [f"{agent}:general"])[0]
        safe_tag = tag.replace(':', '_').replace('/', '_')
        
        target_file = self.base / agent / to_layer / "temporal" / f"{safe_tag}.json"
        
        data = {"tag": tag, "agent": agent, "events": []}
        if target_file.exists():
            with open(target_file) as f:
                data = json.load(f)
        
        # 添加迁移标记
        event["migrated_from"] = from_layer
        event["migrated_at"] = datetime.now().isoformat()
        
        data["events"].append(event)
        
        with open(target_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取记忆系统统计"""
        stats = {}
        
        for agent in self.AGENTS:
            agent_stats = {}
            total_memories = 0
            
            for layer in self.LAYERS:
                temporal_dir = self.base / agent / layer / "temporal"
                if temporal_dir.exists():
                    count = len(list(temporal_dir.glob("*.json")))
                    agent_stats[layer] = count
                    total_memories += count
                else:
                    agent_stats[layer] = 0
            
            agent_stats["total"] = total_memories
            stats[agent] = agent_stats
        
        return stats


def main():
    import sys
    
    memory = UnifiedMemory()
    
    if len(sys.argv) < 2:
        print("统一记忆管理系统 v2.0")
        print()
        print("用法:")
        print("  python3 memory.py write '内容' [--agent kiki] [--tags 优化,代码]")
        print("  python3 memory.py migrate [--agent kiki]")
        print("  python3 memory.py stats")
        print()
        print("示例:")
        print("  python3 memory.py write '优化了数据库查询性能' --agent kiki --tags 优化,性能")
        print("  python3 memory.py write '执行部署脚本' --agent coco --tags 部署,脚本")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "write":
        if len(sys.argv) < 3:
            print("请提供内容")
            return
        
        content = sys.argv[2]
        agent = None
        tags = None
        
        # 解析参数
        for i, arg in enumerate(sys.argv):
            if arg == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
            elif arg == "--tags" and i + 1 < len(sys.argv):
                tags = sys.argv[i + 1].split(",")
        
        result = memory.write(content, agent=agent, tags=tags)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "migrate":
        agent = None
        for i, arg in enumerate(sys.argv):
            if arg == "--agent" and i + 1 < len(sys.argv):
                agent = sys.argv[i + 1]
        
        count = memory.migrate_layers(agent)
        print(f"✅ 迁移完成: {count} 条记忆")
    
    elif cmd == "stats":
        stats = memory.get_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
