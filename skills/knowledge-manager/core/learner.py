#!/usr/bin/env python3
"""
Knowledge Manager - 文档学习引擎
负责解析文档、提取知识、存储到记忆系统
"""

import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class DocumentLearner:
    """文档学习引擎：将文档转化为结构化知识"""
    
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.home() / ".openclaw/workspace"
        self.docs_path = self.base_path / "docs"
        # 使用优化后的知识库存储路径
        self.agents_path = Path.home() / ".openclaw/agents"
        # 新的知识库路径: ~/.openclaw/agents/{agent}/knowledge/tagmemo/
        self.knowledge_dir = "knowledge"
        self.tagmemo_dir = "tagmemo"
        
        # Agent领域关键词映射
        self.domain_keywords = {
            "iris": ["出海", "临床", "FDA", "CtQ", "QTLs", "GCP", "监查", "试验", "伦理", "IND", "多中心"],
            "dreamnova": ["推演", "分析", "预测", "方案对比", "风险评估", "模拟", "验证", "权衡"],
            "kiki": ["优化", "代码", "重构", "性能", "架构", "技术债务", "设计模式", "最佳实践"],
            "luna": ["记忆", "检索", "归档", "整理", "历史", "回顾", "沉淀", "知识库"],
            "nova": ["系统", "协调", "路由", "决策", "配置", "管理", "调度", "监控"]
        }
    
    def ingest(self, file_path: str, context: Dict = None) -> Dict:
        """
        学习一个文档
        
        Args:
            file_path: 文档路径
            context: {
                "source": "user_upload",
                "trigger": "学习",
                "agent_hint": "iris",  # 可选
                "tags": ["出海", "临床"],
                "user_id": "user_001"
            }
        
        Returns:
            学习结果字典
        """
        context = context or {}
        print(f"📚 开始学习文档: {file_path}")
        
        try:
            # 1. 解析文档
            content = self._parse_document(file_path)
            if not content:
                return {"status": "error", "message": "无法解析文档"}
            
            # 2. 判断属于哪个Agent的领域
            agent = self._detect_agent_domain(content, context.get("agent_hint"))
            print(f"🎯 识别为 {agent} 领域知识")
            
            # 3. 提取关键知识片段
            chunks = self._extract_knowledge_chunks(content)
            print(f"🧩 提取 {len(chunks)} 个知识片段")
            
            # 4. 保存原始文档
            doc_path = self._save_original(content, file_path, agent, context.get("tags", []))
            print(f"📂 保存原始文档: {doc_path}")
            
            # 5. 保存到TagMemo（轻量记忆）
            saved_memories = []
            for i, chunk in enumerate(chunks):
                memory_id = self._save_to_tagmemo(agent, chunk, doc_path, i)
                saved_memories.append(memory_id)
            print(f"💾 保存到TagMemo: {len(saved_memories)} 条记录")
            
            # 6. 更新知识索引
            self._update_knowledge_index(agent, doc_path, chunks, context)
            print(f"📇 更新知识索引")
            
            # 7. 生成学习报告
            knowledge_id = self._generate_knowledge_id(file_path)
            
            return {
                "status": "success",
                "knowledge_id": knowledge_id,
                "agent": agent,
                "extracted_chunks": len(chunks),
                "stored_locations": {
                    "original": str(doc_path),
                    "memories": f"agents/{agent}/mid/temporal/",
                    "index": f"agents/{agent}/workspace/knowledge_index.md"
                },
                "chunks_preview": [c["title"] for c in chunks[:5]],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ 学习失败: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _parse_document(self, file_path: str) -> str:
        """解析文档内容"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 根据文件类型解析
        suffix = path.suffix.lower()
        
        if suffix == '.md':
            return path.read_text(encoding='utf-8')
        elif suffix == '.txt':
            return path.read_text(encoding='utf-8')
        elif suffix in ['.docx', '.doc']:
            # 简化处理，实际应该使用python-docx
            return self._parse_docx_simple(path)
        elif suffix == '.pdf':
            # 简化处理，实际应该使用PyPDF2
            return self._parse_pdf_simple(path)
        else:
            # 尝试作为文本读取
            try:
                return path.read_text(encoding='utf-8')
            except:
                raise ValueError(f"不支持的文件格式: {suffix}")
    
    def _parse_docx_simple(self, path: Path) -> str:
        """简单解析DOCX（解压后读取xml）"""
        import zipfile
        try:
            with zipfile.ZipFile(path) as z:
                xml_content = z.read('word/document.xml')
                # 简单提取文本
                text = xml_content.decode('utf-8', errors='ignore')
                # 使用正则提取w:t标签内容
                import re
                texts = re.findall(r'<w:t[^>]*>([^<]+)</w:t>', text)
                return ' '.join(texts)
        except Exception as e:
            return f"[DOCX解析简化版] 文件: {path.name}"
    
    def _parse_pdf_simple(self, path: Path) -> str:
        """
        PDF解析
        
        优先使用PyPDF2或pdfplumber（如果已安装）
        否则使用简单的文本提取作为fallback
        """
        # 尝试使用pdfplumber（推荐，对中文支持更好）
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n'.join(text_parts)
        except ImportError:
            pass
        
        # 尝试使用PyPDF2
        try:
            import PyPDF2
            text_parts = []
            with open(path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
            return '\n'.join(text_parts)
        except ImportError:
            pass
        
        # Fallback：使用pdftotext命令行工具（如果已安装）
        try:
            import subprocess
            result = subprocess.run(
                ['pdftotext', str(path), '-'],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0 and result.stdout:
                return result.stdout
        except:
            pass
        
        # 最后fallback：提示信息
        return f"""[PDF文件: {path.name}]

注意：PDF解析需要安装额外依赖：
  方法1: pip install pdfplumber  (推荐，中文支持好)
  方法2: pip install PyPDF2      (纯Python，无需额外依赖)
  方法3: 安装poppler-utils       (使用pdftotext命令)

请安装后重试学习此文档。

文件路径: {path}
文件大小: {path.stat().st_size} bytes
"""
    
    def _detect_agent_domain(self, content: str, hint: str = None) -> str:
        """判断内容属于哪个Agent的领域"""
        # 如果用户明确指定，优先使用
        if hint and hint in self.domain_keywords:
            return hint
        
        # 自动检测
        scores = {}
        for agent, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[agent] = score
        
        # 如果没有匹配，默认使用iris（假设临床文档较多）
        if max(scores.values()) == 0:
            return "iris"
        
        return max(scores, key=scores.get)
    
    def _extract_knowledge_chunks(self, content: str) -> List[Dict]:
        """从文档中提取知识片段"""
        chunks = []
        
        # 按章节分割（Markdown格式）
        sections = re.split(r'\n##+\s+', content)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # 提取标题（第一行）
            lines = section.strip().split('\n')
            title = lines[0][:50] if lines else f"片段{i+1}"
            
            # 提取内容
            body = '\n'.join(lines[1:]) if len(lines) > 1 else section
            
            # 限制长度
            if len(body) > 1000:
                body = body[:1000] + "..."
            
            # 提取关键词
            keywords = self._extract_keywords(body)
            
            # 计算重要性（简单启发式）
            importance = self._calculate_importance(body, keywords)
            
            chunks.append({
                "id": f"chunk_{i}",
                "title": title,
                "content": body,
                "keywords": keywords,
                "importance": importance,
                "char_count": len(body)
            })
        
        # 按重要性排序，只保留前10个最重要的
        chunks.sort(key=lambda x: x["importance"], reverse=True)
        return chunks[:10]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单实现：提取专有名词和短语
        # 实际应该使用NLP库
        keywords = []
        
        # 提取英文缩写（全大写）
        acronyms = re.findall(r'\b[A-Z]{2,}\b', text)
        keywords.extend(acronyms)
        
        # 提取带引号的术语
        quoted = re.findall(r'「([^」]+)」|"([^"]+)"', text)
        for match in quoted:
            keywords.extend([m for m in match if m])
        
        # 去重并限制数量
        return list(set(keywords))[:10]
    
    def _calculate_importance(self, text: str, keywords: List[str]) -> float:
        """计算片段重要性"""
        score = 0.0
        
        # 有关键词加分
        score += len(keywords) * 0.5
        
        # 长度适中加分（太短没内容，太长难消化）
        length = len(text)
        if 200 < length < 800:
            score += 2.0
        elif length >= 800:
            score += 1.0
        
        # 包含关键句型加分
        if any(phrase in text for phrase in ["重要的是", "关键是", "核心", "必须"]):
            score += 1.5
        
        return min(score, 10.0)  # 最高10分
    
    def _save_original(self, content: str, original_path: str, 
                       agent: str, tags: List[str]) -> Path:
        """保存原始文档"""
        # 确定存储位置
        category = self._determine_category(tags, agent)
        target_dir = self.docs_path / category
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_name = Path(original_path).stem
        filename = f"{original_name}_{timestamp}.md"
        
        # 保存
        doc_path = target_dir / filename
        
        # 添加元数据头
        metadata = f"""---
agent: {agent}
category: {category}
tags: {json.dumps(tags)}
source: {original_path}
learned_at: {datetime.now().isoformat()}
---

"""
        doc_path.write_text(metadata + content, encoding='utf-8')
        
        return doc_path
    
    def _determine_category(self, tags: List[str], agent: str) -> str:
        """根据标签和Agent确定分类"""
        tag_map = {
            "clinical": ["临床", "试验", "出海", "FDA", "GCP"],
            "regulatory": ["法规", "合规", "注册", "申报"],
            "technical": ["技术", "代码", "架构", "系统"],
            "training": ["培训", "学习", "教程"]
        }
        
        for category, keywords in tag_map.items():
            if any(keyword in ' '.join(tags) for keyword in keywords):
                return category
        
        # 默认按Agent分类
        agent_category_map = {
            "iris": "clinical",
            "kiki": "technical",
            "dreamnova": "analysis",
            "luna": "knowledge",
            "nova": "system"
        }
        
        return agent_category_map.get(agent, "general")
    
    def _save_to_tagmemo(self, agent: str, chunk: Dict, 
                         doc_path: Path, index: int) -> str:
        """保存到TagMemo"""
        # 构建TagMemo存储路径（使用新的knowledge/tagmemo结构）
        tagmemo_dir = self.agents_path / agent / self.knowledge_dir / self.tagmemo_dir
        tagmemo_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成记忆ID
        memory_id = f"km_{datetime.now().strftime('%Y%m%d')}_{index:03d}"
        
        # 构建记忆数据
        memory_data = {
            "id": memory_id,
            "content": f"{chunk['title']}\n\n{chunk['content']}",
            "metadata": {
                "source": str(doc_path),
                "agent": agent,
                "chunk_id": chunk['id'],
                "keywords": chunk['keywords'],
                "importance": chunk['importance'],
                "tags": chunk['keywords'] + ["知识", "学习"],
                "timestamp": datetime.now().isoformat(),
                "source_type": "knowledge_manager"
            }
        }
        
        # 保存为JSON
        memory_file = tagmemo_dir / f"{memory_id}.json"
        memory_file.write_text(json.dumps(memory_data, ensure_ascii=False, indent=2))
        
        return memory_id
    
    def _update_knowledge_index(self, agent: str, doc_path: Path, 
                                chunks: List[Dict], context: Dict):
        """更新知识索引（同时保存到workspace和knowledge/index）"""
        # 主索引路径（workspace下，向后兼容）
        index_dir_workspace = self.agents_path / agent / "workspace"
        index_dir_workspace.mkdir(parents=True, exist_ok=True)
        index_path_workspace = index_dir_workspace / "knowledge_index.md"
        
        # 新索引路径（knowledge/index下，更清晰）
        index_dir_knowledge = self.agents_path / agent / self.knowledge_dir / "index"
        index_dir_knowledge.mkdir(parents=True, exist_ok=True)
        index_path_knowledge = index_dir_knowledge / "knowledge_index.md"
        
        # 读取现有索引或创建新索引
        if index_path_workspace.exists():
            existing_content = index_path_workspace.read_text(encoding='utf-8')
        else:
            existing_content = f"# {agent.upper()} 知识库索引\n\n自动生成的知识文档索引。\n\n"
        
        # 生成新条目
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = f"""
## {doc_path.stem}

- **路径**: {doc_path}
- **添加时间**: {timestamp}
- **知识片段数**: {len(chunks)}
- **关键词**: {', '.join(sum([c['keywords'] for c in chunks], []))[:100]}...

### 片段预览
"""
        for chunk in chunks[:3]:  # 只显示前3个
            new_entry += f"- **{chunk['title']}** (重要性: {chunk['importance']:.1f})\n"
        
        new_entry += "\n---\n"
        
        # 追加到索引（同时保存到两个位置）
        updated_content = existing_content + new_entry
        index_path_workspace.write_text(updated_content, encoding='utf-8')
        index_path_knowledge.write_text(updated_content, encoding='utf-8')
    
    def _generate_knowledge_id(self, file_path: str) -> str:
        """生成知识ID"""
        hash_input = f"{file_path}_{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]


# 测试入口
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python learner.py <文件路径> [agent_hint]")
        sys.exit(1)
    
    file_path = sys.argv[1]
    agent_hint = sys.argv[2] if len(sys.argv) > 2 else None
    
    learner = DocumentLearner()
    result = learner.ingest(file_path, {
        "source": "cli",
        "trigger": "学习",
        "agent_hint": agent_hint,
        "tags": ["自动学习"]
    })
    
    print("\n" + "="*50)
    print("学习结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
