#!/usr/bin/env python3
"""
Agent 需求分析模块
每月分析对话，识别是否需要新业务 Agent
Version: 1.0.0
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict

class AgentDemandAnalyzer:
    """Agent 需求分析器"""
    
    # 核心系统 Agent (不应建议删除)
    CORE_AGENTS = ['nova', 'kiki', 'coco', 'luna', 'dreamnova']
    
    # 系统级 Agent 关键词（才建议创建新 Agent）
    # 业务知识通过 Nova 记忆 + 技能扩展即可
    SYSTEM_AGENT_DOMAINS = {
        'orchestrator': {
            'name': '协调者',
            'keywords': ['多 Agent 协调', '分布式任务', '集群管理'],
            'reason': '需要协调其他 Agents'
        },
        'security': {
            'name': '安全专家',
            'keywords': ['安全审计', '渗透测试', '加密', '权限'],
            'reason': '涉及系统安全'
        },
        'data_engineer': {
            'name': '数据工程师',
            'keywords': ['大数据', 'ETL', '数据仓库', '数据治理'],
            'reason': '需要专业数据能力'
        },
        'ml_engineer': {
            'name': 'ML 工程师',
            'keywords': ['模型训练', '特征工程', '模型部署', 'MLOps'],
            'reason': '需要机器学习专业能力'
        }
    }
    
    # 业务领域知识（通过 Nova 记忆即可，不创建 Agent）
    BUSINESS_KNOWLEDGE = {
        'clinical': ['临床试验', 'GCP', '患者', 'TQC'],  # 已有 Iris
        'finance': ['预算', '成本', '财务', '报销'],       # Nova 记忆即可
        'legal': ['合同', '法务', '合规', '法律'],         # Nova 记忆即可
        'marketing': ['市场', '营销', '品牌'],              # Nova 记忆即可
        'hr': ['招聘', '面试', '绩效'],                    # Nova 记忆即可
    }
    
    def __init__(self):
        self.base = Path.home() / ".openclaw"
        self.daily_notes_dir = self.base / "shared/notes/daily"
        self.min_conversation_threshold = 10  # 最少对话次数才分析
        self.min_topic_percentage = 0.20      # 主题占比超过20%才建议
    
    def analyze_period(self, days: int = 30) -> Dict:
        """
        分析最近N天的对话内容
        
        Args:
            days: 分析多少天的数据 (默认30天)
        """
        today = datetime.now()
        start_date = today - timedelta(days=days)
        
        period_str = f"{start_date.strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}"
        
        # 收集所有 DailyNote
        conversations = []
        current = start_date
        
        while current <= today:
            note_file = self.daily_notes_dir / f"{current.strftime('%Y-%m-%d')}.md"
            if note_file.exists():
                content = note_file.read_text()
                conversations.extend(self._extract_conversations(content))
            current += timedelta(days=1)
        
        if len(conversations) < self.min_conversation_threshold:
            return {
                "period": period_str,
                "status": "insufficient_data",
                "message": f"对话数量不足 ({len(conversations)} < {self.min_conversation_threshold})",
                "suggestion": "积累更多对话后重新分析"
            }
        
        # 分析主题分布
        topic_dist = self._analyze_topics(conversations)
        
        # 检查是否需要新 Agent
        suggestions = self._identify_agent_gaps(topic_dist, conversations)
        
        return {
            "period": period_str,
            "total_conversations": len(conversations),
            "topic_distribution": topic_dist,
            "suggestions": suggestions,
            "analysis_date": datetime.now().isoformat()
        }
    
    def analyze_last_month(self) -> Dict:
        """分析上个月的对话 (兼容旧接口)"""
        return self.analyze_period(days=30)
    
    def _extract_conversations(self, content: str) -> List[str]:
        """从 DailyNote V6 提取对话内容"""
        conversations = []
        
        # 匹配 V6 格式: **内容:** 任务描述
        # 也匹配旧的 - 条目格式
        
        # 方法1: V6 格式 **内容:** xxx
        v6_items = re.findall(r'\*\*内容:\*\* (.+?)(?:\n\*\*|$)', content)
        conversations.extend(v6_items)
        
        # 方法2: 旧格式 - 内容 (时间)
        old_items = re.findall(r'- (.+?) \*\(\d{2}:\d{2}\)\*', content)
        conversations.extend(old_items)
        
        # 方法3: 列表项 - 开头的内容
        list_items = re.findall(r'^- (.+)$', content, re.MULTILINE)
        conversations.extend([i for i in list_items if len(i) > 10])
        
        return [c.strip() for c in conversations if len(c.strip()) > 5]
    
    def _analyze_topics(self, conversations: List[str]) -> Dict[str, float]:
        """分析对话主题分布"""
        topic_counts = defaultdict(int)
        
        for conv in conversations:
            conv_lower = conv.lower()
            matched = False
            
            for domain, template in self.BUSINESS_AGENT_TEMPLATES.items():
                for keyword in template['keywords']:
                    if keyword.lower() in conv_lower:
                        topic_counts[domain] += 1
                        matched = True
                        break
            
            if not matched:
                # 检查核心系统主题
                if any(kw in conv_lower for kw in ['系统', '任务', 'wave', 'haven']):
                    topic_counts['system'] += 1
                elif any(kw in conv_lower for kw in ['代码', '优化', '重构', '性能']):
                    topic_counts['optimization'] += 1
                elif any(kw in conv_lower for kw in ['执行', '脚本', '部署', '运行']):
                    topic_counts['execution'] += 1
                else:
                    topic_counts['other'] += 1
        
        # 计算百分比
        total = sum(topic_counts.values())
        return {k: round(v/total, 3) for k, v in sorted(topic_counts.items(), key=lambda x: -x[1])}
    
    def _identify_agent_gaps(self, topic_dist: Dict, conversations: List[str]) -> List[Dict]:
        """识别系统级 Agent 缺口 (业务需求不创建 Agent)"""
        suggestions = []
        
        for domain, info in self.SYSTEM_AGENT_DOMAINS.items():
            # 计算该领域在对话中的占比
            keywords = info['keywords']
            matched_count = sum(
                1 for conv in conversations
                if any(kw in conv for kw in keywords)
            )
            percentage = matched_count / len(conversations) if conversations else 0
            
            # 只有系统级需求且占比高才建议
            if percentage >= self.min_topic_percentage:
                # 检查是否已有对应系统 Agent
                existing = self._check_existing_system_agent(domain)
                
                if not existing:
                    suggestions.append({
                        "domain": domain,
                        "type": "system",  # 标记为系统级
                        "confidence": round(min(percentage * 2, 0.95), 2),
                        "percentage": percentage,
                        "reason": f"{percentage*100:.0f}%的对话涉及系统级功能「{info['name']}」，"
                                  f"建议创建专职 Agent。\n"
                                  f"   原因: {info['reason']}",
                        "suggested_name": domain.capitalize(),
                        "role": info['name'],
                        "keywords": keywords[:3]
                    })
        
        # 业务需求不创建 Agent，但会提示 Nova 积累知识
        business_topics = []
        for domain, keywords in self.BUSINESS_KNOWLEDGE.items():
            matched_count = sum(
                1 for conv in conversations
                if any(kw in conv for kw in keywords)
            )
            percentage = matched_count / len(conversations) if conversations else 0
            
            if percentage >= self.min_topic_percentage:
                business_topics.append({
                    "domain": domain,
                    "percentage": percentage,
                    "suggestion": f"建议 Nova 积累「{domain}」领域知识"
                })
        
        # 如果有业务需求但无系统级需求，给出知识积累建议
        if business_topics and not suggestions:
            return [{
                "type": "knowledge",
                "message": "检测到高频业务话题",
                "topics": business_topics,
                "recommendation": "业务知识由 Nova 记忆即可，无需创建新 Agent"
            }]
        
        return sorted(suggestions, key=lambda x: -x.get('confidence', 0))
    
    def _check_existing_system_agent(self, domain: str) -> Optional[str]:
        """检查是否已有对应的系统级 Agent"""
        # 核心系统 Agent 检查
        core_agents = {
            'security': ['sentinel', 'guardian', 'security'],
            'data_engineer': ['data', 'db', 'warehouse'],
            'ml_engineer': ['ml', 'ai', 'model'],
            'orchestrator': ['orch', 'coordinator', 'scheduler']
        }
        
        expected_names = core_agents.get(domain, [domain])
        
        for expected in expected_names:
            agent_dir = self.base / f"agents/{expected.lower()}"
            if agent_dir.exists():
                return expected.lower()
        
        return None
    
    def generate_report(self, analysis: Dict) -> str:
        """生成可读的分析报告"""
        if analysis.get('status') == 'insufficient_data':
            return f"📊 {analysis['period']} Agent 需求分析\n\n{analysis['message']}"
        
        report = f"""📊 {analysis['period']} Agent 需求分析报告
{'='*50}

📈 对话统计
- 总对话数: {analysis['total_conversations']}
- 分析日期: {analysis['analysis_date'][:10]}

📊 主题分布
"""
        
        for topic, pct in analysis['topic_distribution'].items():
            bar = '█' * int(pct * 20)
            report += f"  {topic:15s} {bar} {pct*100:5.1f}%\n"
        
        # 系统级 Agent 建议
        system_suggestions = [s for s in analysis.get('suggestions', []) if s.get('type') == 'system']
        knowledge_suggestions = [s for s in analysis.get('suggestions', []) if s.get('type') == 'knowledge']
        
        if system_suggestions:
            report += f"\n💡 建议新增系统级 Agent\n"
            for i, sug in enumerate(system_suggestions, 1):
                report += f"""
{i}. 【{sug['suggested_name']}】{sug['role']}
   置信度: {'🟢' if sug['confidence'] > 0.8 else '🟡'} {sug['confidence']*100:.0f}%
   理由: {sug['reason']}
   相关关键词: {', '.join(sug['keywords'])}
"""
            
            report += f"\n👉 如需部署，请回复: '部署 {system_suggestions[0]['suggested_name']}'\n"
        
        elif knowledge_suggestions:
            report += f"\n📚 业务知识积累建议\n"
            for sug in knowledge_suggestions:
                report += f"\n{sug['message']}:\n"
                for topic in sug['topics']:
                    report += f"  • {topic['domain']}: {topic['percentage']*100:.0f}% - {topic['suggestion']}\n"
            report += f"\n💡 业务知识由 Nova 记忆即可，无需创建新 Agent\n"
        
        else:
            report += "\n✅ 当前配置充足，无需新增 Agent 或知识\n"
        
        report += "\n" + "="*50 + "\n"
        report += "📝 说明: 仅系统级功能建议创建新 Agent\n"
        report += "       业务知识通过 Nova 记忆 + 技能扩展即可\n"
        
        return report


def main():
    import sys
    
    analyzer = AgentDemandAnalyzer()
    
    if len(sys.argv) < 2:
        print("Agent 需求分析模块")
        print()
        print("用法:")
        print("  python3 agent_analyzer.py analyze      # 分析上个月")
        print("  python3 agent_analyzer.py report       # 生成报告")
        print()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "analyze":
        result = analyzer.analyze_last_month()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif cmd == "report":
        result = analyzer.analyze_last_month()
        print(analyzer.generate_report(result))
    
    else:
        print(f"未知命令: {cmd}")


if __name__ == "__main__":
    main()
