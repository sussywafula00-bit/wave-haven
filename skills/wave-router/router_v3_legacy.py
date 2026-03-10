#!/usr/bin/env python3
"""
Nova 浪潮路由器 - 基于 Tag 的智能调度系统
"""

import json
import subprocess
from pathlib import Path

LUNA_TAGMEMO = Path.home() / ".openclaw/agents/luna/workspace/skills/tagmemo-memory/agent.py"

class WaveRouter:
    """浪潮路由器 - 基于 Tag 语义分析的智能调度"""
    
    def __init__(self):
        self.complexity_threshold = 0.7
        self.width_threshold = 0.2
    
    def extract_tags(self, text: str) -> list:
        """快速提取 Tags 和信号词"""
        # 时间词
        time_patterns = ["昨天", "上次", "之前", "去年", "前几天", "刚才", "当时"]
        # 记忆相关词
        memory_patterns = ["记得", "当时", "怎么解决", "曾经", "回忆", "上次"]
        # 复杂决策词
        complex_patterns = ["分析", "评估", "对比", "利弊", "权衡", "推演", "架构", "设计"]
        # 摇摆信号词（辩证）
        hesitation_patterns = ["但是", "然而", "不过", "也许", "可能", "虽然", "尽管", "另一方面"]
        
        found = []
        all_patterns = time_patterns + memory_patterns + complex_patterns + hesitation_patterns
        for pattern in all_patterns:
            if pattern in text:
                found.append(pattern)
        return found
    
    def analyze_intent(self, text: str) -> dict:
        """深度分析用户意图"""
        tags = self.extract_tags(text)
        
        # 复杂度评估
        complexity = 0.0
        if any(w in text for w in ["分析", "评估", "推演", "设计", "架构", "方案"]):
            complexity += 0.3
        if len(tags) > 3:
            complexity += 0.2
        if len(text) > 50:
            complexity += 0.2
        
        # 语义宽度（发散程度）
        width = 0.0
        if "，" in text or "。" in text:
            width += 0.05 * text.count("，")
        if any(w in text for w in ["还有", "另外", "顺便", "以及", "同时"]):
            width += 0.2
        
        # 摇摆信号（辩证需求）
        hesitation_signals = ["但是", "然而", "不过", "也许", "可能", "虽然", "尽管", "另一方面"]
        has_hesitation = any(s in text for s in hesitation_signals)
        
        # 时序需求
        time_signals = ["上次", "之前", "当时", "曾经", "以前", "去年", "前几天"]
        has_temporal = any(s in text for s in time_signals)
        
        # 执行需求
        exec_signals = ["执行", "运行", "脚本", "部署", "安装", "配置"]
        has_exec = any(s in text for s in exec_signals)
        
        return {
            "complexity": min(complexity, 1.0),
            "width": min(width, 1.0),
            "has_hesitation": has_hesitation,
            "has_temporal": has_temporal,
            "has_exec": has_exec,
            "tags": tags
        }
    
    def route(self, user_input: str) -> dict:
        """智能路由决策"""
        analysis = self.analyze_intent(user_input)
        
        # 决策逻辑（优先级排序）
        
        # 1. 时序查询 → Luna Tag 拓扑检索
        if analysis["has_temporal"] or "记忆" in user_input or "轨迹" in user_input:
            return {
                "action": "查询记忆轨迹",
                "target": "Luna",
                "mode": "tagmemo_trajectory",
                "context": analysis,
                "message": "📚 检测到记忆查询，启动 Luna Tag 拓扑检索...",
                "command": f"python3 {LUNA_TAGMEMO} query 相关标签"
            }
        
        # 2. 高复杂度 + 聚焦 → DreamNova 深度推演
        elif analysis["complexity"] > 0.6 and analysis["width"] < 0.3:
            return {
                "action": "启动梦境推演",
                "target": "DreamNova",
                "budget": "deep",
                "context": analysis,
                "message": "🌙 检测到复杂推演需求，启动 DreamNova Tag 拓扑推演..."
            }
        
        # 3. 摇摆信号 + 发散 → 辩证检索
        elif analysis["has_hesitation"] or analysis["width"] > 0.5:
            return {
                "action": "辩证分析",
                "target": "DreamNova",
                "mode": "polarized_view",
                "context": analysis,
                "message": "⚖️ 检测到辩证需求，准备对冲视角..."
            }
        
        # 4. 执行任务 → Coco
        elif analysis["has_exec"]:
            return {
                "action": "执行任务",
                "target": "Coco",
                "context": analysis,
                "message": "⚡ 执行任务，交给 Coco..."
            }
        
        # 5. 简单任务 → Nova 直接处理
        else:
            return {
                "action": "直接处理",
                "target": "Nova",
                "context": analysis,
                "message": "🌟 直接处理中..."
            }

def main():
    import sys
    router = WaveRouter()
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        result = router.route(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"error": "No input provided"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
