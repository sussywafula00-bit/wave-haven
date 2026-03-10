#!/usr/bin/env python3
"""
Knowledge Manager - 知识查询引擎
负责查询知识，支持轻量查询（TagMemo）和深度查询（完整文档）
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class KnowledgeQuerier:
    """知识查询引擎：按需加载知识"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home() / ".openclaw/workspace"
        self.docs_path = self.base_path / "docs"
        # 使用优化后的知识库存储路径
        self.agents_path = Path.home() / ".openclaw/agents"
        self.knowledge_dir = "knowledge"
        self.tagmemo_dir = "tagmemo"
        
        # Agent领域映射
        self.agent_domains = {
            "iris": ["出海", "临床", "FDA", "CtQ", "QTLs", "GCP", "监查", "试验"],
            "dreamnova": ["推演", "分析", "预测", "方案对比", "风险评估"],
            "kiki": ["优化", "代码", "重构", "性能", "架构"],
            "luna": ["记忆", "检索", "归档", "整理", "历史"],
            "nova": ["系统", "协调", "路由", "决策", "配置"]
        }
    
    def query(self, question: str, agent: str = None, 
              depth: str = "auto") -> Dict:
        """
        查询知识
        
        Args:
            question: 用户问题
            agent: 指定Agent（可选）
            depth: 查询深度
                   - "light": 只查TagMemo片段（快，省token）
                   - "deep": 读取完整文档（详细，费token）
                   - "auto": 自动判断（默认）
        
        Returns:
            {
                "status": "success",
                "answer": "回答内容",
                "source": "tagmemo" / "document",
                "confidence": 0.85,
                "references": ["doc1.md", "doc2.md"],
                "agent": "iris",
                "query_info": {...}
            }
        """
        print(f"🔍 查询知识: {question}")
        
        try:
            # 1. 分析查询
            query_info = self._analyze_query(question)
            print(f"📊 查询分析: {query_info['intent']} | 复杂度: {query_info['complexity']}")
            
            # 2. 确定目标Agent
            target_agent = agent or self._detect_agent_from_query(question)
            print(f"🎯 目标Agent: {target_agent}")
            
            # 3. 自动判断查询深度
            if depth == "auto":
                depth = self._decide_depth(question, query_info)
            print(f"📏 查询深度: {depth}")
            
            # 4. 执行查询
            if depth == "light":
                result = self._light_query(target_agent, question, query_info)
            else:
                result = self._deep_query(target_agent, question, query_info)
            
            # 5. 包装结果
            result.update({
                "status": "success",
                "agent": target_agent,
                "query_info": query_info,
                "timestamp": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            print(f"❌ 查询失败: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "question": question
            }
    
    def _analyze_query(self, question: str) -> Dict:
        """分析查询意图"""
        info = {
            "intent": "unknown",
            "keywords": [],
            "complexity": "simple",
            "has_numbers": False,
            "has_temporal": False
        }
        
        # 检测意图类型
        if re.search(r"什么是|什么是|定义|解释一下", question):
            info["intent"] = "definition"
        elif re.search(r"怎么做|如何|流程|步骤", question):
            info["intent"] = "procedure"
        elif re.search(r"为什么|原因|理由", question):
            info["intent"] = "explanation"
        elif re.search(r"比较|对比|区别|差异", question):
            info["intent"] = "comparison"
        elif re.search(r"列出|有哪些|给我|请提供", question):
            info["intent"] = "list"
        else:
            info["intent"] = "general"
        
        # 提取关键词
        info["keywords"] = self._extract_query_keywords(question)
        
        # 判断复杂度
        word_count = len(question)
        if word_count > 30 or info["intent"] in ["procedure", "comparison"]:
            info["complexity"] = "complex"
        elif word_count > 15:
            info["complexity"] = "moderate"
        else:
            info["complexity"] = "simple"
        
        # 检测是否有数字或时间
        info["has_numbers"] = bool(re.search(r'\d+', question))
        info["has_temporal"] = bool(re.search(r'时间|日期|时候|多久|天|月|年', question))
        
        return info
    
    def _extract_query_keywords(self, question: str) -> List[str]:
        """提取查询关键词"""
        keywords = []
        
        # 提取专业术语（英文缩写）
        acronyms = re.findall(r'\b[A-Z]{2,}\b', question)
        keywords.extend(acronyms)
        
        # 提取引号内容
        quoted = re.findall(r'「([^」]+)」|"([^"]+)"', question)
        for match in quoted:
            keywords.extend([m for m in match if m])
        
        # 提取长度大于2的词（简单实现）
        words = re.findall(r'[\u4e00-\u9fa5]{2,}|[a-zA-Z]{3,}', question)
        keywords.extend(words)
        
        return list(set(keywords))
    
    def _detect_agent_from_query(self, question: str) -> str:
        """从查询中检测目标Agent"""
        scores = {}
        for agent, keywords in self.agent_domains.items():
            score = sum(1 for keyword in keywords if keyword in question)
            scores[agent] = score
        
        # 如果没有匹配，默认返回iris
        if max(scores.values()) == 0:
            return "iris"
        
        return max(scores, key=scores.get)
    
    def _decide_depth(self, question: str, query_info: Dict) -> str:
        """自动判断查询深度"""
        # 简单定义问题 → light
        if query_info["intent"] == "definition" and query_info["complexity"] == "simple":
            return "light"
        
        # 有明确关键词的问题 → light
        if len(query_info["keywords"]) >= 2 and query_info["complexity"] in ["simple", "moderate"]:
            return "light"
        
        # 流程、对比、复杂问题 → deep
        if query_info["intent"] in ["procedure", "comparison"]:
            return "deep"
        
        # 默认light
        return "light"
    
    def _light_query(self, agent: str, question: str, 
                     query_info: Dict) -> Dict:
        """轻量查询：只查TagMemo"""
        print(f"📱 执行轻量查询（TagMemo）...")
        
        # 1. 搜索TagMemo
        memories = self._search_tagmemo(agent, question, query_info, limit=5)
        
        if not memories:
            # 如果没找到，自动降级到deep查询
            print(f"⚠️ TagMemo未找到相关内容，自动降级到深度查询")
            return self._deep_query(agent, question, query_info)
        
        # 2. 判断内容是否足够回答
        if self._is_sufficient(memories, question):
            # 3. 合成答案
            answer = self._synthesize_from_memories(memories, question)
            
            return {
                "answer": answer,
                "source": "tagmemo",
                "confidence": self._calculate_confidence(memories),
                "references": [m.get("source", "unknown") for m in memories],
                "memories_count": len(memories),
                "method": "light"
            }
        else:
            # 内容不够，降级到deep查询
            print(f"⚠️ TagMemo内容不够详细，自动降级到深度查询")
            return self._deep_query(agent, question, query_info)
    
    def _deep_query(self, agent: str, question: str, 
                    query_info: Dict) -> Dict:
        """深度查询：读取完整文档"""
        print(f"📚 执行深度查询（完整文档）...")
        
        # 1. 查找相关文档
        docs = self._find_relevant_docs(agent, question, query_info)
        
        if not docs:
            return {
                "answer": f"抱歉，在{agent}的知识库中没有找到相关内容。",
                "source": "none",
                "confidence": 0.0,
                "references": [],
                "method": "deep"
            }
        
        # 2. 读取文档内容
        contents = []
        for doc_path in docs[:2]:  # 最多读2个文档
            content = self._read_document(doc_path)
            if content:
                contents.append({
                    "path": str(doc_path),
                    "content": content[:3000]  # 限制长度
                })
        
        # 3. 生成答案
        answer = self._generate_from_documents(contents, question)
        
        return {
            "answer": answer,
            "source": "document",
            "confidence": 0.9,
            "references": [c["path"] for c in contents],
            "documents_count": len(contents),
            "method": "deep"
        }
    
    def _search_tagmemo(self, agent: str, question: str, 
                        query_info: Dict, limit: int = 5) -> List[Dict]:
        """搜索TagMemo"""
        memories = []
        
        # TagMemo路径
        # TagMemo路径（使用新的knowledge/tagmemo结构）
        tagmemo_dir = self.agents_path / agent / self.knowledge_dir / self.tagmemo_dir
        
        if not tagmemo_dir.exists():
            return memories
        
        # 关键词匹配
        keywords = query_info["keywords"]
        
        # 遍历所有记忆文件
        for memory_file in tagmemo_dir.glob("*.json"):
            try:
                data = json.loads(memory_file.read_text())
                content = data.get("content", "")
                metadata = data.get("metadata", {})
                
                # 计算匹配度
                match_score = 0
                for keyword in keywords:
                    if keyword.lower() in content.lower():
                        match_score += 1
                    if keyword in metadata.get("keywords", []):
                        match_score += 2
                
                if match_score > 0:
                    memories.append({
                        "id": data.get("id"),
                        "content": content,
                        "source": metadata.get("source"),
                        "keywords": metadata.get("keywords", []),
                        "importance": metadata.get("importance", 0),
                        "match_score": match_score,
                        "timestamp": metadata.get("timestamp")
                    })
            except:
                continue
        
        # 按匹配度和重要性排序
        memories.sort(key=lambda x: (x["match_score"], x["importance"]), reverse=True)
        
        return memories[:limit]
    
    def _is_sufficient(self, memories: List[Dict], question: str) -> bool:
        """判断记忆内容是否足够回答"""
        if not memories:
            return False
        
        # 总内容长度
        total_length = sum(len(m["content"]) for m in memories)
        
        # 简单定义问题，200字符足够
        if len(question) < 20 and total_length >= 200:
            return True
        
        # 一般问题，500字符足够
        if total_length >= 500:
            return True
        
        return False
    
    def _synthesize_from_memories(self, memories: List[Dict], 
                                   question: str) -> str:
        """从记忆片段合成答案"""
        # 简单拼接（实际应该用LLM生成）
        parts = []
        
        for i, memory in enumerate(memories[:3]):  # 最多用3个
            parts.append(f"{memory['content']}")
        
        answer = "\n\n".join(parts)
        
        # 如果太长，截断
        if len(answer) > 1500:
            answer = answer[:1500] + "..."
        
        return answer
    
    def _calculate_confidence(self, memories: List[Dict]) -> float:
        """计算置信度"""
        if not memories:
            return 0.0
        
        # 基于匹配度和重要性计算
        total_score = sum(m["match_score"] + m.get("importance", 0) for m in memories)
        confidence = min(total_score / 10, 0.95)  # 最高0.95
        
        return round(confidence, 2)
    
    def _find_relevant_docs(self, agent: str, question: str, 
                            query_info: Dict) -> List[Path]:
        """查找相关文档"""
        docs = []
        
        # 1. 从知识索引查找
        index_path = self.agents_path / agent / "workspace" / "knowledge_index.md"
        if index_path.exists():
            # 简单解析索引文件
            index_content = index_path.read_text()
            # 提取文档路径
            for line in index_content.split('\n'):
                if '**路径**' in line or '路径:' in line:
                    path_match = re.search(r'/(docs/.+\.md)', line)
                    if path_match:
                        doc_path = self.base_path / path_match.group(1)
                        if doc_path.exists():
                            docs.append(doc_path)
        
        # 2. 直接搜索docs目录
        keywords = query_info["keywords"]
        for doc_file in self.docs_path.rglob("*.md"):
            try:
                content = doc_file.read_text()
                match_count = sum(1 for k in keywords if k in content)
                if match_count >= 2:
                    docs.append((doc_file, match_count))
            except:
                continue
        
        # 去重并排序
        seen = set()
        unique_docs = []
        for item in docs:
            if isinstance(item, tuple):
                doc_path, score = item
            else:
                doc_path = item
                score = 1
            
            if str(doc_path) not in seen:
                seen.add(str(doc_path))
                unique_docs.append((doc_path, score))
        
        unique_docs.sort(key=lambda x: x[1], reverse=True)
        return [d[0] for d in unique_docs[:5]]
    
    def _read_document(self, doc_path: Path) -> str:
        """读取文档内容"""
        try:
            return doc_path.read_text(encoding='utf-8')
        except:
            return ""
    
    def _generate_from_documents(self, contents: List[Dict], 
                                  question: str) -> str:
        """从文档生成答案"""
        # 简单实现：返回最相关的文档内容
        if not contents:
            return "未找到相关内容"
        
        # 返回第一个文档的摘要
        main_doc = contents[0]
        content = main_doc["content"]
        
        # 提取前1000字符作为答案
        answer = content[:1000]
        if len(content) > 1000:
            answer += "...\n\n[文档内容较长，以上是节选]"
        
        return answer


# 测试入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python querier.py '<查询内容>' [agent] [depth]")
        print("示例: python querier.py 'CtQ是什么' iris light")
        sys.exit(1)
    
    question = sys.argv[1]
    agent = sys.argv[2] if len(sys.argv) > 2 else None
    depth = sys.argv[3] if len(sys.argv) > 3 else "auto"
    
    querier = KnowledgeQuerier()
    result = querier.query(question, agent, depth)
    
    print("\n" + "="*50)
    print("查询结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
