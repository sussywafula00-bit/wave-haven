#!/usr/bin/env python3
"""
Knowledge Flow - 知识流自动化 V1.0
浪潮完成 → 自动提取知识 → Knowledge Manager 学习 → 后续检索
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import sys

# 添加事件总线
sys.path.insert(0, str(Path(__file__).parent.parent / "wave-event-bus"))
from bus import emit_event, EventType

class KnowledgeFlow:
    """知识流自动化"""
    
    def __init__(self):
        self.base_path = Path.home() / ".openclaw/shared/knowledge"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.wave_dir = Path.home() / ".openclaw/shared/waves"
        self.knowledge_manager = Path.home() / ".openclaw/workspace_shared/skills/knowledge-manager/agent.py"
    
    def process_wave_completion(self, wave_id: str) -> Dict:
        """处理浪潮完成，自动提取知识"""
        print(f"📚 处理浪潮知识沉淀: {wave_id}")
        
        wave_file = self.wave_dir / f"{wave_id}.json"
        if not wave_file.exists():
            return {"status": "failed", "message": f"Wave {wave_id} not found"}
        
        with open(wave_file, 'r', encoding='utf-8') as f:
            wave = json.load(f)
        
        # 1. 提取知识
        knowledge = self._extract_knowledge(wave)
        
        # 2. 保存知识文档
        knowledge_file = self._save_knowledge(wave_id, knowledge)
        
        # 3. 生成标签
        tags = self._generate_tags(knowledge)
        
        # 4. 更新知识索引
        self._update_knowledge_index(wave_id, knowledge, tags)
        
        # 5. 发射事件
        emit_event(EventType.KNOWLEDGE_LEARNED, wave_id, data={
            "knowledge_file": str(knowledge_file),
            "tags": tags,
            "key_points": knowledge.get("key_points", [])
        })
        
        print(f"   ✅ 知识已沉淀: {knowledge_file}")
        
        return {
            "status": "success",
            "wave_id": wave_id,
            "knowledge_file": str(knowledge_file),
            "tags": tags,
            "key_points_count": len(knowledge.get("key_points", []))
        }
    
    def _extract_knowledge(self, wave: Dict) -> Dict:
        """从浪潮中提取知识"""
        task = wave.get("task", "")
        subtasks = wave.get("subtasks", [])
        
        # 提取关键信息
        key_points = []
        decisions = []
        lessons = []
        
        # 从任务描述中提取
        if "决策" in task or "决定" in task:
            decisions.append({
                "type": "task_decision",
                "content": task,
                "timestamp": wave.get("created_at")
            })
        
        # 从子任务结果中提取
        for subtask in subtasks:
            desc = subtask.get("desc", "")
            result = subtask.get("result", {})
            agent = subtask.get("agent")
            
            # 提取决策
            if result and isinstance(result, dict):
                if "decision" in result:
                    decisions.append({
                        "type": "subtask_decision",
                        "agent": agent,
                        "content": result["decision"],
                        "context": desc
                    })
                
                # 提取关键输出
                if "output" in result:
                    key_points.append({
                        "agent": agent,
                        "content": result["output"][:200] if len(str(result["output"])) > 200 else result["output"]
                    })
                
                # 提取经验教训
                if "lesson" in result or "经验" in desc:
                    lessons.append({
                        "agent": agent,
                        "content": result.get("lesson", desc)
                    })
        
        # 提取技术关键词
        tech_keywords = self._extract_tech_keywords(task + " " + str(subtasks))
        
        return {
            "task": task,
            "wave_id": wave["wave_id"],
            "created_at": wave.get("created_at"),
            "completed_at": wave.get("completed_at"),
            "agents_involved": wave.get("agents", []),
            "key_points": key_points,
            "decisions": decisions,
            "lessons": lessons,
            "tech_keywords": tech_keywords,
            "subtask_summary": {
                "total": len(subtasks),
                "completed": len([s for s in subtasks if s.get("status") == "completed"]),
                "failed": len([s for s in subtasks if s.get("status") == "failed"])
            }
        }
    
    def _extract_tech_keywords(self, text: str) -> List[str]:
        """提取技术关键词"""
        keywords = []
        
        patterns = {
            r'Python|python': 'Python',
            r'JavaScript|JS|js|Node\.js': 'JavaScript',
            r'API|api|GraphQL|REST': 'API',
            r'数据库|database|MySQL|PostgreSQL|MongoDB': '数据库',
            r'架构|architecture|微服务|microservice': '架构',
            r'AI|人工智能|机器学习|ML': 'AI',
            r'临床|clinical|COPD|试验': '临床',
            r'SOP|流程|标准': 'SOP',
            r'风险|risk|评估': '风险管理',
            r'浪潮|wave|agent': '浪潮系统'
        }
        
        for pattern, keyword in patterns.items():
            if re.search(pattern, text) and keyword not in keywords:
                keywords.append(keyword)
        
        return keywords
    
    def _save_knowledge(self, wave_id: str, knowledge: Dict) -> Path:
        """保存知识文档"""
        knowledge_file = self.base_path / "auto" / f"{wave_id}_knowledge.md"
        knowledge_file.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""# 知识摘要: {knowledge['task'][:50]}

**浪潮ID:** {knowledge['wave_id']}  
**完成时间:** {knowledge.get('completed_at', 'N/A')}  
**参与Agent:** {', '.join(knowledge.get('agents_involved', []))}

## 关键要点

"""
        
        for i, point in enumerate(knowledge.get('key_points', []), 1):
            content += f"{i}. **{point.get('agent', 'System')}**: {point.get('content', '')}\n"
        
        if knowledge.get('decisions'):
            content += "\n## 关键决策\n\n"
            for decision in knowledge['decisions']:
                content += f"- **{decision.get('type')}**: {decision.get('content', '')}\n"
        
        if knowledge.get('lessons'):
            content += "\n## 经验教训\n\n"
            for lesson in knowledge['lessons']:
                content += f"- **{lesson.get('agent', 'Team')}**: {lesson.get('content', '')}\n"
        
        if knowledge.get('tech_keywords'):
            content += f"\n## 技术标签\n\n{' '.join(['#' + k for k in knowledge['tech_keywords']])}\n"
        
        content += f"""
## 执行统计

- 总子任务: {knowledge['subtask_summary']['total']}
- 完成: {knowledge['subtask_summary']['completed']}
- 失败: {knowledge['subtask_summary']['failed']}
"""
        
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return knowledge_file
    
    def _generate_tags(self, knowledge: Dict) -> List[str]:
        """生成知识标签"""
        tags = []
        
        # 从Agent生成
        tags.extend([f"agent:{a}" for a in knowledge.get('agents_involved', [])])
        
        # 从技术关键词生成
        tags.extend(knowledge.get('tech_keywords', []))
        
        # 从任务类型生成
        task = knowledge.get('task', '')
        if "分析" in task or "评估" in task:
            tags.append("类型:分析")
        if "决策" in task or "决定" in task:
            tags.append("类型:决策")
        if "部署" in task or "实施" in task:
            tags.append("类型:执行")
        
        return list(set(tags))
    
    def _update_knowledge_index(self, wave_id: str, knowledge: Dict, tags: List[str]):
        """更新知识索引"""
        index_file = self.base_path / "knowledge_index.json"
        
        index = {}
        if index_file.exists():
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
        
        index[wave_id] = {
            "task": knowledge['task'][:100],
            "completed_at": knowledge.get('completed_at'),
            "tags": tags,
            "agents": knowledge.get('agents_involved', []),
            "key_points_count": len(knowledge.get('key_points', [])),
            "file": f"auto/{wave_id}_knowledge.md"
        }
        
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
    
    def search_knowledge(self, query: str, tags: List[str] = None) -> List[Dict]:
        """搜索知识"""
        index_file = self.base_path / "knowledge_index.json"
        
        if not index_file.exists():
            return []
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        results = []
        
        for wave_id, entry in index.items():
            score = 0
            
            # 文本匹配
            if query.lower() in entry.get('task', '').lower():
                score += 10
            
            # 标签匹配
            if tags:
                entry_tags = entry.get('tags', [])
                score += len(set(tags) & set(entry_tags)) * 5
            
            if score > 0:
                results.append({
                    "wave_id": wave_id,
                    "score": score,
                    **entry
                })
        
        return sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    
    def get_knowledge_stats(self) -> Dict:
        """获取知识统计"""
        index_file = self.base_path / "knowledge_index.json"
        
        if not index_file.exists():
            return {"total": 0, "tags": [], "agents": []}
        
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
        
        all_tags = set()
        all_agents = set()
        
        for entry in index.values():
            all_tags.update(entry.get('tags', []))
            all_agents.update(entry.get('agents', []))
        
        return {
            "total": len(index),
            "tags": sorted(list(all_tags)),
            "agents": sorted(list(all_agents)),
            "last_updated": datetime.now().isoformat()
        }

def main():
    """命令行入口"""
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = args.get("action")
    
    flow = KnowledgeFlow()
    
    if action == "process":
        result = flow.process_wave_completion(args.get("wave_id"))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "search":
        result = flow.search_knowledge(
            args.get("query", ""),
            args.get("tags", [])
        )
        print(json.dumps({"status": "success", "results": result}, ensure_ascii=False, indent=2))
    
    elif action == "stats":
        result = flow.get_knowledge_stats()
        print(json.dumps({"status": "success", "stats": result}, ensure_ascii=False, indent=2))
    
    else:
        print(json.dumps({"status": "failed", "message": f"Unknown action: {action}"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
