#!/usr/bin/env python3
"""
Agent 路由系统 - Nova 到 Luna 的协作
当 Nova 遇到临床试验相关内容时，自动路由给 Luna
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict

class AgentRouter:
    """Agent 智能路由"""
    
    # Luna 的专业领域关键词
    LUNA_KEYWORDS = [
        "临床试验", "GCP", "伦理审查", "方案偏离", "SAE",
        "研究中心", "监查", "稽查", "入排标准", "受试者",
        "知情同意", "数据管理", "统计分析", "临床试验项目",
        "CRO", "申办方", "研究者", "伦理委员会", "TQC",
        "COPD", "哮喘", "糖尿病", "高血压", "肿瘤", "III期", "II期"
    ]
    
    def __init__(self):
        self.luna_memory_path = Path.home() / ".openclaw/agents/luna/workspace/memory/agents/luna/mid/temporal"
        self.nova_memory_path = Path.home() / ".openclaw/agents/luna/workspace/memory/agents/nova/mid/temporal"
    
    def should_route_to_luna(self, content: str) -> bool:
        """判断是否应该路由给 Luna"""
        content_lower = content.lower()
        for keyword in self.LUNA_KEYWORDS:
            if keyword.lower() in content_lower:
                return True
        return False
    
    def route_memory(self, content: str, source: str = "nova", tags: list = None) -> Dict:
        """
        路由记忆到正确的 Agent
        
        Returns:
            {
                "agent": "luna" | "nova",
                "action": "routed" | "local",
                "message": str
            }
        """
        if self.should_route_to_luna(content):
            # 保存到 Luna 的记忆
            self._save_to_luna(content, source, tags)
            return {
                "agent": "luna",
                "action": "routed",
                "message": f"📋 临床试验相关内容已路由给 Luna 处理\n   内容: {content[:50]}..."
            }
        else:
            return {
                "agent": "nova",
                "action": "local",
                "message": f"✅ Nova 本地处理: {content[:50]}..."
            }
    
    def _save_to_luna(self, content: str, source: str, tags: list):
        """保存记忆到 Luna"""
        from datetime import datetime

        self.luna_memory_path.mkdir(parents=True, exist_ok=True)

        # 确定 Tag
        tag = "clinical:trial/management"
        if tags:
            tag = tags[0] if tags else tag

        memory_file = self.luna_memory_path / f"{tag.replace(':', '_').replace('/', '_')}.json"

        # 加载或创建
        data = {"tag": tag, "agent": "luna", "events": []}
        if memory_file.exists():
            data = json.load(open(memory_file))

        now = datetime.now()
        event = {
            "content": content,
            "agent": "luna",
            "source": source,
            "ts": now.isoformat(),
            "tags": tags or [tag],
            "year": now.year,
            "month": now.month,
            "week": now.isocalendar()[1],
            "day_of_week": now.weekday(),
            "routed_from": "nova"
        }

        data["events"].append(event)

        with open(memory_file, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def query_luna(self, query: str) -> Optional[str]:
        """
        Nova 查询 Luna 的专业知识

        Returns:
            Luna 的回复或 None
        """
        if not self.should_route_to_luna(query):
            return None

        # 搜索 Luna 的记忆
        results = []
        for f in self.luna_memory_path.glob("*.json"):
            try:
                data = json.load(open(f))
                for event in data.get("events", []):
                    if any(kw in event.get("content", "") for kw in self.LUNA_KEYWORDS):
                        if any(kw in query for kw in self.LUNA_KEYWORDS):
                            results.append(event["content"])
            except:
                continue

        if results:
            return f"🌙 Luna: 根据我的知识...\n\n相关记忆:\n" + "\n".join([f"  • {r[:80]}..." for r in results[:3]])

        return "🌙 Luna: 收到，这是一个相关问题。我会记录下来并在后续跟进。"


def main():
    import sys
    
    router = AgentRouter()
    
    if len(sys.argv) < 2:
        print("Agent 路由系统")
        print()
        print("用法:")
        print("  python3 agent_router.py route '内容'     # 路由记忆")
        print("  python3 agent_router.py query '问题'     # 查询 Iris")
        print()
        print("Iris 专业领域:")
        print("  临床试验、GCP、伦理审查、方案偏离、研究中心...")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "route" and len(sys.argv) > 2:
        content = sys.argv[2]
        result = router.route_memory(content)
        print(result["message"])
        print(f"\n路由决策: {result['agent']} ({result['action']})")
    
    elif cmd == "query" and len(sys.argv) > 2:
        query = sys.argv[2]
        response = router.query_luna(query)
        if response:
            print(response)
        else:
            print("ℹ️ 这不是相关问题，Nova 自行处理")
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
