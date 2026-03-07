#!/usr/bin/env python3
"""
Haven Knowledge Module
知识管理增强功能
Version: 1.0.0
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter

class HavenKnowledgeManager:
    """Haven 知识管理器"""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".openclaw/shared/SYSTEM/tagmemo"
        self.storage_dir = storage_dir
        self.knowledge_dir = Path.home() / ".openclaw/shared/SYSTEM/knowledge"
        self.notes_dir = Path.home() / ".openclaw/shared/SYSTEM/notes"
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """语义搜索知识"""
        results = []
        query_lower = query.lower()
        query_keywords = set(query_lower.split())
        
        # 搜索所有知识文件
        all_files = []
        for directory in [self.storage_dir, self.knowledge_dir, self.notes_dir]:
            if directory.exists():
                all_files.extend(directory.rglob("*.json"))
                all_files.extend(directory.rglob("*.md"))
        
        for file_path in all_files:
            try:
                content = self._extract_content(file_path)
                if not content:
                    continue
                
                # 计算相似度分数
                score = self._calculate_similarity(query_lower, query_keywords, content, file_path)
                
                if score > 0:
                    results.append({
                        "file": str(file_path.relative_to(Path.home())),
                        "title": self._extract_title(content, file_path),
                        "preview": self._generate_preview(content, query_lower),
                        "score": score,
                        "tags": self._extract_tags(content),
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
                    })
            except Exception as e:
                continue
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def _extract_content(self, file_path: Path) -> str:
        """提取文件内容"""
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 尝试提取文本字段
                    if isinstance(data, dict):
                        text_fields = []
                        for key in ['content', 'text', 'description', 'summary', 'message']:
                            if key in data:
                                text_fields.append(str(data[key]))
                        return ' '.join(text_fields)
                    elif isinstance(data, list) and len(data) > 0:
                        return str(data[0])
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except:
            return ""
        return ""
    
    def _calculate_similarity(self, query: str, query_keywords: set, content: str, file_path: Path) -> float:
        """计算相似度分数 (0-100)"""
        content_lower = content.lower()
        score = 0.0
        
        # 1. 完全匹配查询词
        if query in content_lower:
            score += 40
        
        # 2. 关键词匹配
        content_words = set(content_lower.split())
        matching_words = query_keywords & content_words
        score += len(matching_words) * 10
        
        # 3. 文件名匹配
        filename = file_path.name.lower()
        if any(kw in filename for kw in query_keywords):
            score += 15
        
        # 4. 时效性加分（最近7天的文件）
        try:
            mtime = file_path.stat().st_mtime
            if datetime.now().timestamp() - mtime < 7 * 24 * 3600:
                score += 5
        except:
            pass
        
        return min(score, 100)
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """提取标题"""
        # 尝试从内容中提取标题
        lines = content.split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Markdown 标题
            if line.startswith('#'):
                return line.lstrip('#').strip()
            # 非空行作为标题
            if line and len(line) < 100:
                return line[:50]
        # 使用文件名
        return file_path.stem[:50]
    
    def _generate_preview(self, content: str, query: str, max_length: int = 100) -> str:
        """生成预览文本"""
        content = content.replace('\n', ' ')
        
        # 尝试找到查询词附近的内容
        query_pos = content.lower().find(query)
        if query_pos >= 0:
            start = max(0, query_pos - 40)
            end = min(len(content), query_pos + len(query) + 40)
            preview = content[start:end]
            if start > 0:
                preview = "..." + preview
            if end < len(content):
                preview = preview + "..."
            return preview[:max_length]
        
        # 返回开头
        return content[:max_length] + "..." if len(content) > max_length else content
    
    def _extract_tags(self, content: str) -> List[str]:
        """提取标签"""
        tags = []
        # 查找 #tag 格式
        tag_pattern = r'#(\w+)'
        matches = re.findall(tag_pattern, content)
        tags.extend(['#' + m for m in matches[:5]])
        return tags
    
    def get_stats(self) -> Dict:
        """获取知识库统计"""
        stats = {
            "total_memories": 0,
            "total_storage_mb": 0.0,
            "by_type": {},
            "recent_7days": 0,
            "recent_30days": 0,
            "top_tags": []
        }
        
        all_files = []
        all_tags = []
        
        for directory in [self.storage_dir, self.knowledge_dir, self.notes_dir]:
            if not directory.exists():
                continue
            
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    try:
                        stat = file_path.stat()
                        stats["total_memories"] += 1
                        stats["total_storage_mb"] += stat.st_size / (1024 * 1024)
                        
                        # 文件类型统计
                        ext = file_path.suffix or "no_ext"
                        stats["by_type"][ext] = stats["by_type"].get(ext, 0) + 1
                        
                        # 时间统计
                        age_days = (datetime.now().timestamp() - stat.st_mtime) / (24 * 3600)
                        if age_days < 7:
                            stats["recent_7days"] += 1
                        if age_days < 30:
                            stats["recent_30days"] += 1
                        
                        # 提取标签
                        content = self._extract_content(file_path)
                        tags = self._extract_tags(content)
                        all_tags.extend(tags)
                        
                    except:
                        continue
        
        # 统计热门标签
        tag_counter = Counter(all_tags)
        stats["top_tags"] = tag_counter.most_common(10)
        
        return stats
    
    def organize(self) -> Dict:
        """整理知识库"""
        result = {
            "analyzed": 0,
            "duplicates_found": 0,
            "orphaned_tags_cleaned": 0,
            "storage_saved_mb": 0.0
        }
        
        # 这里可以实现更复杂的整理逻辑
        # 例如：合并重复、清理孤立标签等
        
        return result
    
    def get_recent(self, days: int = 7, limit: int = 20) -> List[Dict]:
        """获取最近的知识"""
        recent = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for directory in [self.storage_dir, self.knowledge_dir, self.notes_dir]:
            if not directory.exists():
                continue
            
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    try:
                        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if mtime > cutoff:
                            content = self._extract_content(file_path)
                            recent.append({
                                "file": str(file_path.relative_to(Path.home())),
                                "title": self._extract_title(content, file_path),
                                "modified": mtime.strftime('%Y-%m-%d %H:%M'),
                                "tags": self._extract_tags(content)
                            })
                    except:
                        continue
        
        # 按时间排序
        recent.sort(key=lambda x: x["modified"], reverse=True)
        return recent[:limit]


if __name__ == "__main__":
    # 测试
    manager = HavenKnowledgeManager()
    
    # 测试搜索
    print("Testing search...")
    results = manager.search("test", top_k=5)
    for r in results:
        print(f"  {r['score']:.0f}% - {r['title'][:30]}")
    
    # 测试统计
    print("\nTesting stats...")
    stats = manager.get_stats()
    print(f"  Total: {stats['total_memories']}")
    print(f"  Storage: {stats['total_storage_mb']:.2f} MB")
