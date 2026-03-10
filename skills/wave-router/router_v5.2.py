#!/usr/bin/env python3
"""
Nova 浪潮路由器 V5.2 - 上下文感知路由增强版
新增：Session Context 上下文管理

Changes in V5.2:
- 添加上下文感知路由
- 支持会话历史追踪
- Agent 粘性保持
- 上下文权重衰减
"""

import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

LUNA_TAGMEMO = Path.home() / ".openclaw/agents/luna/workspace/skills/tagmemo-memory/agent.py"
KNOWLEDGE_MANAGER = Path.home() / ".openclaw/workspace/skills/knowledge-manager/agent.py"

class WaveRouterV5:
    """浪潮路由器 V5.2 - 上下文感知路由"""
    
    def __init__(self):
        self.complexity_threshold = 0.7
        self.width_threshold = 0.2
        
        # V5.2 新增：上下文配置
        self.context_config = {
            "max_rounds": 3,          # 保持3轮对话
            "decay_factor": 0.7,      # 权重衰减系数
            "stickiness_threshold": 0.6  # Agent粘性阈值
        }
        
        # 上下文存储路径
        self.context_file = Path.home() / ".openclaw/shared/SYSTEM/waves/session_contexts.json"
        
        # 语义组配置
        self.semantic_groups = {
            "技术栈": ["API", "架构", "设计", "代码", "数据库", "性能", "优化", "GraphQL", "REST", "微服务"],
            "项目管理": ["项目", "会议", "决策", "进度", "风险", "团队", "沟通"],
            "学习成长": ["学习", "阅读", "思考", "笔记", "总结", "反思", "研究"],
            "执行操作": ["执行", "部署", "测试", "重构", "修复", "完成", "启动"],
            "记忆查询": ["记忆", "轨迹", "回顾", "历史", "上次", "之前", "曾经"],
            "推演分析": ["分析", "评估", "对比", "利弊", "权衡", "推演", "方案"],
            "知识管理": ["知识", "学习", "查询", "什么是", "告诉我", "查找", "搜索", "文档"]
        }
        
        # 知识管理关键词
        self.knowledge_learn_keywords = ["学习", "笔记", "总结", "上传", "添加知识", "保存文档"]
        self.knowledge_query_keywords = ["什么是", "什么是", "告诉我", "查找", "搜索知识", "查询", "了解", "解释一下", "定义"]
    
    # ==================== V5.2 新增：上下文管理 ====================
    
    def _load_context(self, session_id: str = None) -> list:
        """加载会话上下文历史"""
        if not session_id:
            return []
        
        if not self.context_file.exists():
            return []
        
        try:
            with open(self.context_file, 'r', encoding='utf-8') as f:
                all_contexts = json.load(f)
                return all_contexts.get(session_id, [])
        except Exception as e:
            print(f"[V5.2] 加载上下文失败: {e}")
            return []
    
    def _save_context(self, session_id: str, user_input: str, decision: dict):
        """保存上下文条目"""
        if not session_id:
            return
        
        try:
            # 加载现有上下文
            all_contexts = {}
            if self.context_file.exists():
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    all_contexts = json.load(f)
            
            # 获取或创建会话上下文
            session_context = all_contexts.get(session_id, [])
            
            # 添加新条目
            entry = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input[:100],  # 截断存储
                "target": decision.get("target"),
                "action": decision.get("action"),
                "mode": decision.get("mode")
            }
            session_context.append(entry)
            
            # V5.2：只保留最近 N 轮
            max_rounds = self.context_config.get("max_rounds", 3)
            if len(session_context) > max_rounds:
                session_context = session_context[-max_rounds:]
            
            all_contexts[session_id] = session_context
            
            # 保存
            self.context_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(all_contexts, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[V5.2] 保存上下文失败: {e}")
    
    def _calculate_context_weights(self, context: list) -> dict:
        """计算上下文权重（时间衰减）"""
        weights = {}
        decay = self.context_config.get("decay_factor", 0.7)
        
        for i, entry in enumerate(reversed(context)):
            target = entry.get("target")
            if target:
                weight = decay ** i  # 指数衰减
                weights[target] = weights.get(target, 0) + weight
        
        return weights
    
    def _adjust_decision(self, decision: dict, context: list) -> dict:
        """V5.2：根据上下文调整决策"""
        if not context or len(context) == 0:
            return decision
        
        # 计算各Agent的上下文权重
        weights = self._calculate_context_weights(context)
        
        if not weights:
            return decision
        
        current_target = decision.get("target")
        last_target = context[-1].get("target")
        
        # V5.2 策略：Agent 粘性
        # 如果上次和这次目标不同，但上次Agent权重高，考虑保持一致
        if last_target and current_target and last_target != current_target:
            last_weight = weights.get(last_target, 0)
            current_weight = weights.get(current_target, 0)
            
            threshold = self.context_config.get("stickiness_threshold", 0.6)
            
            # 如果上次Agent权重显著高于当前决策，且输入类似（简单启发式）
            if last_weight > threshold and last_weight > current_weight * 1.5:
                # 检查是否是追问或继续讨论（简单启发式）
                last_input = context[-1].get("user_input", "")
                # 如果输入较短，可能是追问
                # 这里可以添加更复杂的NLP判断
                pass
        
        # V5.2：添加上下文信息到决策
        decision["context_aware"] = True
        decision["context_history"] = len(context)
        decision["context_weights"] = weights
        
        return decision
    
    # ==================== V5.2 结束 ====================

    def extract_tags(self, text: str) -> list:
        """智能提取Tags"""
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
            if re.search(pattern, text) and tag not in found:
                found.append(tag)
        
        return found

    def detect_semantic_groups(self, text: str) -> list:
        """检测激活的语义组"""
        activated = []
        text_lower = text.lower()
        
        for group_name, group_tags in self.semantic_groups.items():
            matches = sum(1 for tag in group_tags if tag.lower() in text_lower)
            if matches >= 1:
                activated.append(group_name)
        
        return activated

    def is_knowledge_intent(self, text: str) -> dict:
        """检测是否为知识管理相关意图"""
        # 检测学习意图
        for keyword in self.knowledge_learn_keywords:
            if keyword in text:
                return {"is_knowledge": True, "type": "learn"}
        
        # 检测查询意图
        for keyword in self.knowledge_query_keywords:
            if keyword in text:
                return {"is_knowledge": True, "type": "query"}
        
        # 特殊模式
        if re.search(r'\b\w+是什么\b', text) or re.search(r'\b什么是\w+\b', text):
            return {"is_knowledge": True, "type": "query"}
        
        if any(w in text for w in ["查找", "搜索", "找一下"]) and len(text) < 30:
            return {"is_knowledge": True, "type": "query"}
        
        return {"is_knowledge": False, "type": "none"}

    def analyze_intent(self, text: str) -> dict:
        """深度意图分析（V5增强版）"""
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
            width += 0.2
        
        # 特殊信号
        signals = {
            "hesitation": any(s in text for s in ["但是", "然而", "不过", "也许", "可能", "虽然"]),
            "temporal": any(s in text for s in ["上次", "之前", "当时", "曾经", "以前", "上周", "最近", "@7d", "@30d"]),
            "exec": any(s in text for s in ["执行", "运行", "脚本", "部署", "安装", "配置"]),
            "memory_query": "记忆查询" in activated_groups or "轨迹" in text,
            "tech_stack": "技术栈" in activated_groups,
            "learning": "学习成长" in activated_groups,
            "knowledge": "知识管理" in activated_groups,
            "multi_agent": "和" in text and any(a in text for a in ["Coco", "DreamNova", "Kiki", "Luna"])
        }
        
        return {
            "complexity": min(complexity, 1.0),
            "width": min(width, 1.0),
            "activated_groups": activated_groups,
            "signals": signals,
            "tags": tags
        }

    # ==================== V5.2 修改：添加上下文参数 ====================
    def route(self, user_input: str, session_id: str = None) -> dict:
        """
        智能路由决策（V5.2 上下文感知增强版）
        
        Args:
            user_input: 用户输入
            session_id: 会话ID（V5.2新增，用于上下文追踪）
        """
        
        # 【V5.2新增】加载上下文
        context = self._load_context(session_id)
        if context:
            print(f"[V5.2] 加载上下文: {len(context)} 轮历史")
        
        # 【V5原有】优先检测知识管理意图
        knowledge_check = self.is_knowledge_intent(user_input)
        if knowledge_check["is_knowledge"]:
            decision = self._route_knowledge(user_input, knowledge_check["type"])
        else:
            # 【V5原有】路由逻辑
            decision = self._route_standard(user_input)
        
        # 【V5.2新增】根据上下文调整决策
        if context:
            decision = self._adjust_decision(decision, context)
            print(f"[V5.2] 上下文调整完成")
        
        # 【V5.2新增】保存上下文
        self._save_context(session_id, user_input, decision)
        
        return decision
    
    def _route_standard(self, user_input: str) -> dict:
        """V5 标准路由逻辑（提取为单独方法）"""
        analysis = self.analyze_intent(user_input)
        signals = analysis["signals"]
        groups = analysis["activated_groups"]
        
        # 构建TagMemo查询命令
        tagmemo_query = ""
        if analysis["tags"]:
            tagmemo_query = "相关标签"
        
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

    def _route_knowledge(self, user_input: str, knowledge_type: str) -> dict:
        """知识管理路由"""
        if knowledge_type == "learn":
            return {
                "action": "知识学习",
                "target": "KnowledgeManager",
                "mode": "learn",
                "type": "knowledge",
                "message": "📚 检测到知识学习意图，启动 Knowledge Manager...",
                "command": f"python3 {KNOWLEDGE_MANAGER} learn",
                "needs_file": True,
                "hint": "请提供要学习的文档路径"
            }
        
        else:  # query
            query_content = user_input
            for keyword in self.knowledge_query_keywords:
                query_content = query_content.replace(keyword, "").strip()
            
            return {
                "action": "知识查询",
                "target": "KnowledgeManager",
                "mode": "query",
                "type": "knowledge",
                "message": "🔍 检测到知识查询意图，启动 Knowledge Manager...",
                "command": f"python3 {KNOWLEDGE_MANAGER} query '{query_content}'",
                "query": query_content
            }


def main():
    import sys
    router = WaveRouterV5()
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
        # V5.2: 支持传入 session_id
        session_id = None
        if "--session" in sys.argv:
            idx = sys.argv.index("--session")
            if idx + 1 < len(sys.argv):
                session_id = sys.argv[idx + 1]
        
        result = router.route(user_input, session_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 演示模式
        print("=== WaveRouter V5.2 演示（上下文感知增强版）===\n")
        
        test_inputs = [
            "上周我们讨论的架构方案怎么样了？",  # 记忆查询 + 时间感知
            "学习一下出海手册",  # 知识学习
            "CtQ是什么？",  # 知识查询
            "帮我执行这个部署脚本",  # 执行
            "分析一下GraphQL和REST的利弊",  # 推演
        ]
        
        print("V5.2 新功能：上下文感知路由")
        print("使用 --session <id> 参数测试上下文追踪\n")
        
        for inp in test_inputs:
            print(f"输入: {inp}")
            result = router.route(inp, session_id="demo_session")
            print(f"路由: {result['target']} | 动作: {result['action']}")
            if result.get('context_aware'):
                print(f"[V5.2] 上下文感知: 历史 {result.get('context_history', 0)} 轮")
            print()


if __name__ == "__main__":
    main()
