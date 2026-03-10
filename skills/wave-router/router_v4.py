#!/usr/bin/env python3
"""
Nova 浪潮路由器 V4.0 - 增强版
集成 TagMemo V4: 语义组、时间感知、智能Tag补全
"""

import json
import subprocess
from pathlib import Path

LUNA_TAGMEMO = Path.home() / ".openclaw/agents/luna/workspace/skills/tagmemo-memory/agent.py"

class WaveRouterV4:
    """浪潮路由器 V4 - 集成TagMemo增强功能"""
    
    def __init__(self):
        self.complexity_threshold = 0.7
        self.width_threshold = 0.2
        
        # 语义组配置（与TagMemo V4同步）
        self.semantic_groups = {
            "技术栈": ["API", "架构", "设计", "代码", "数据库", "性能", "优化", "GraphQL", "REST", "微服务"],
            "项目管理": ["项目", "会议", "决策", "进度", "风险", "团队", "沟通"],
            "学习成长": ["学习", "阅读", "思考", "笔记", "总结", "反思", "研究"],
            "执行操作": ["执行", "部署", "测试", "重构", "修复", "完成", "启动"],
            "记忆查询": ["记忆", "轨迹", "回顾", "历史", "上次", "之前", "曾经"],
            "推演分析": ["分析", "评估", "对比", "利弊", "权衡", "推演", "方案"]
        }
    
    def extract_tags(self, text: str) -> list:
        """智能提取Tags（集成V4 AI补全）"""
        # 基础关键词匹配
        time_patterns = ["昨天", "上次", "之前", "去年", "前几天", "刚才", "当时", "上周", "最近", "@7d"]
        memory_patterns = ["记得", "当时", "怎么解决", "曾经", "回忆", "上次", "轨迹"]
        complex_patterns = ["分析", "评估", "对比", "利弊", "权衡", "推演", "架构", "设计", "方案"]
        hesitation_patterns = ["但是", "然而", "不过", "也许", "可能", "虽然", "尽管", "另一方面"]
        
        found = []
        all_patterns = time_patterns + memory_patterns + complex_patterns + hesitation_patterns
        for pattern in all_patterns:
            if pattern in text:
                found.append(pattern)
        
        # AI增强：识别技术栈
        tech_patterns = {
            r'GraphQL|graphql': 'GraphQL',
            r'microservice|微服务': '微服务',
            r'API|api': 'API',
            r'架构|architecture': '架构'
        }
        for pattern, tag in tech_patterns.items():
            import re
            if re.search(pattern, text) and tag not in found:
                found.append(tag)
        
        return found
    
    def detect_semantic_groups(self, text: str) -> list:
        """检测激活的语义组"""
        activated = []
        text_lower = text.lower()
        
        for group_name, group_tags in self.semantic_groups.items():
            # 计算匹配度
            matches = sum(1 for tag in group_tags if tag.lower() in text_lower)
            if matches >= 1:  # 至少1个匹配
                activated.append(group_name)
        
        return activated
    
    def analyze_intent(self, text: str) -> dict:
        """深度意图分析（V4增强版）"""
        tags = self.extract_tags(text)
        activated_groups = self.detect_semantic_groups(text)
        
        # 复杂度评估
        complexity = 0.0
        if any(w in text for w in self.semantic_groups["推演分析"]):
            complexity += 0.4
        if "技术栈" in activated_groups:
            complexity += 0.2
        if len(tags) > 3:
            complexity += 0.2
        if len(text) > 50:
            complexity += 0.2
        
        # 语义宽度
        width = 0.0
        if "，" in text or "。" in text:
            width += 0.05 * text.count("，")
        if any(w in text for w in ["还有", "另外", "顺便", "以及", "同时"]):
            width += 0.2
        if len(activated_groups) > 1:
            width += 0.2  # 多语义组 = 发散思维
        
        # 特殊信号
        signals = {
            "hesitation": any(s in text for s in ["但是", "然而", "不过", "也许", "可能", "虽然"]),
            "temporal": any(s in text for s in ["上次", "之前", "当时", "曾经", "以前", "上周", "最近", "@7d", "@30d"]),
            "exec": any(s in text for s in ["执行", "运行", "脚本", "部署", "安装", "配置"]),
            "memory_query": "记忆查询" in activated_groups or "轨迹" in text,
            "tech_stack": "技术栈" in activated_groups,
            "learning": "学习成长" in activated_groups,
            "multi_agent": "和" in text and any(a in text for a in ["Coco", "DreamNova", "Kiki", "Luna"])
        }
        
        return {
            "complexity": min(complexity, 1.0),
            "width": min(width, 1.0),
            "activated_groups": activated_groups,
            "signals": signals,
            "tags": tags
        }
    
    def route(self, user_input: str) -> dict:
        """智能路由决策（V4增强版）"""
        analysis = self.analyze_intent(user_input)
        signals = analysis["signals"]
        groups = analysis["activated_groups"]
        
        # 构建TagMemo查询命令
        tagmemo_query = ""
        if analysis["tags"]:
            tagmemo_query = "相关标签"
        
        # 决策逻辑
        
        # 1. 记忆查询 + 时间感知 → Luna TagMemo
        if signals["memory_query"] or signals["temporal"]:
            return {
                "action": "记忆轨迹查询",
                "target": "Luna",
                "mode": "tagmemo_time_aware",
                "use_semantic_group": True,
                "context": analysis,
                "message": f"📚 检测到{'时间感知' if signals['temporal'] else ''}记忆查询，启动 Luna TagMemo...",
                "groups": groups,
                "command": f"python3 {LUNA_TAGMEMO} query \"{user_input}\" nova mid --time --group"
            }
        
        # 2. 技术栈讨论 + 高复杂度 → DreamNova 推演
        elif signals["tech_stack"] and analysis["complexity"] > 0.5:
            return {
                "action": "技术架构推演",
                "target": "DreamNova",
                "budget": "deep" if analysis["complexity"] > 0.8 else "medium",
                "mode": "tech_architecture",
                "context": analysis,
                "message": "🌙 检测到技术架构推演需求，启动 DreamNova...",
                "groups": groups
            }
        
        # 3. 多Agent协作
        elif signals["multi_agent"]:
            return {
                "action": "多Agent协作",
                "target": "WaveManager",
                "mode": "multi_agent",
                "context": analysis,
                "message": "🌊 检测到多Agent协作需求，启动浪潮协调...",
                "agents": [a for a in ["Coco", "DreamNova", "Kiki", "Luna"] if a in user_input]
            }
        
        # 4. 学习成长 → Kiki
        elif signals["learning"]:
            return {
                "action": "学习优化",
                "target": "Kiki",
                "mode": "learning_optimization",
                "context": analysis,
                "message": "📈 检测到学习成长需求，启动 Kiki...",
                "groups": groups
            }
        
        # 5. 摇摆信号 + 发散 → DreamNova 辩证
        elif signals["hesitation"] or analysis["width"] > 0.5:
            return {
                "action": "辩证分析",
                "target": "DreamNova",
                "mode": "polarized_view",
                "context": analysis,
                "message": "⚖️ 检测到辩证需求，准备对冲视角...",
                "groups": groups
            }
        
        # 6. 执行任务 → Coco
        elif signals["exec"]:
            return {
                "action": "执行任务",
                "target": "Coco",
                "context": analysis,
                "message": "⚡ 执行任务，交给 Coco...",
                "groups": groups
            }
        
        # 7. 简单任务 → Nova 直接处理
        else:
            return {
                "action": "直接处理",
                "target": "Nova",
                "context": analysis,
                "message": "🌟 直接处理中...",
                "groups": groups
            }

def main():
    import sys
    router = WaveRouterV4()
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        result = router.route(user_input)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 演示模式
        print("=== WaveRouter V4.0 演示 ===\n")
        
        test_inputs = [
            "上周我们讨论的架构方案怎么样了？",
            "我想分析一下GraphQL和REST的利弊",
            "帮我执行这个部署脚本",
            "学习一下如何优化数据库性能",
            "Coco和DreamNova一起完成这个任务"
        ]
        
        for inp in test_inputs:
            print(f"输入: {inp}")
            result = router.route(inp)
            print(f"路由: {result['target']} | 动作: {result['action']}")
            print(f"激活语义组: {result.get('groups', [])}")
            print()

if __name__ == "__main__":
    main()
