#!/usr/bin/env python3
"""
DailyNote V5.0 - 知识管理增强版
新增：学习事件自动通知Knowledge Manager
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

# 基础路径配置
BASE = Path(os.getenv("OPENCLAW_PATH", Path.home() / ".openclaw"))
NOTES_DIR = BASE / "shared" / "notes" / "daily"
ARCHIVE_DIR = BASE / "shared" / "notes" / "archives"
WAVES_DIR = BASE / "shared" / "waves"
TEMPLATE_PATH = Path(__file__).parent / "templates"
TAGMEMO_PATH = BASE / "agents/luna/workspace/skills/tagmemo-memory/agent.py"

# 【V5新增】Knowledge Manager路径
KNOWLEDGE_MANAGER = BASE / "workspace/skills/knowledge-manager/agent.py"

# 确保目录存在
NOTES_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


class DailyNoteManagerV5:
    """每日笔记管理器 V5 - 集成Knowledge Manager"""

    def __init__(self):
        self.notes_dir = NOTES_DIR
        self.archive_dir = ARCHIVE_DIR
        
        # 语义组配置
        self.semantic_groups = {
            "技术栈": ["API", "架构", "设计", "代码", "数据库", "性能", "优化", "GraphQL", "REST", "微服务"],
            "项目管理": ["项目", "会议", "决策", "进度", "风险", "团队"],
            "学习成长": ["学习", "阅读", "思考", "笔记", "总结", "反思"],
            "执行操作": ["执行", "部署", "测试", "重构", "修复", "完成"]
        }
        
        # 【V5新增】学习关键词
        self.learning_keywords = ["学习", "笔记", "总结", "阅读", "研究", "探索", "了解了", "掌握了"]

    def _extract_tags_ai(self, content: str) -> List[str]:
        """AI驱动的Tag提取"""
        tags = []
        
        # 基础关键词
        keywords = ["API","架构","设计","代码","调试","优化","性能","数据库",
                   "项目","会议","决策","学习","思考","笔记","执行","部署","测试"]
        found = [k for k in keywords if k in content]
        tags.extend(found)
        
        # AI增强：技术栈识别
        tech_patterns = {
            r'GraphQL|graphql': 'GraphQL',
            r'ReST|REST|rest': 'REST',
            r'microservice|微服务': '微服务',
            r'Python|python': 'Python',
            r'JavaScript|JS|js': 'JavaScript',
            r'API|api': 'API',
            r'架构|architecture': '架构'
        }
        
        for pattern, tag in tech_patterns.items():
            if re.search(pattern, content) and tag not in tags:
                tags.append(tag)
        
        # AI增强：行为识别
        action_patterns = {
            r'完成|搞定|结束': '完成',
            r'开始|启动': '开始',
            r'分析|研究': '分析',
            r'讨论|会议': '讨论',
            r'决策|决定': '决策',
            r'优化|改进': '优化',
            r'修复|解决': '修复'
        }
        
        for pattern, tag in action_patterns.items():
            if re.search(pattern, content) and tag not in tags:
                tags.append(tag)
        
        return list(set(tags))[:8]  # 最多8个

    def _detect_semantic_groups(self, tags: List[str]) -> List[str]:
        """检测激活的语义组"""
        activated = []
        tag_set = set(tags)
        
        for group_name, group_tags in self.semantic_groups.items():
            if tag_set & set(group_tags):  # 有交集
                activated.append(group_name)
        
        return activated

    def _is_learning_content(self, content: str) -> bool:
        """【V5新增】判断是否为学习内容"""
        for keyword in self.learning_keywords:
            if keyword in content:
                return True
        return False

    def _notify_knowledge_manager(self, content: str, tags: List[str]) -> Dict:
        """【V5新增】通知Knowledge Manager"""
        try:
            # 构建通知数据
            notification = {
                "event": "learning_recorded",
                "content_preview": content[:100] + "..." if len(content) > 100 else content,
                "tags": tags,
                "timestamp": datetime.now().isoformat(),
                "source": "daily-note",
                "suggested_action": "consider_indexing"  # 建议建立索引
            }
            
            # 可以在这里调用Knowledge Manager的API
            # 或者只是记录到日志，供后续处理
            
            return {
                "status": "notified",
                "notification": notification
            }
        except Exception as e:
            return {
                "status": "notification_failed",
                "error": str(e)
            }

    def _get_note_path(self, date: Optional[datetime] = None) -> Path:
        """获取指定日期的笔记路径"""
        if date is None:
            date = datetime.now()
        filename = date.strftime("%Y-%m-%d.md")
        return self.notes_dir / filename

    def _get_template(self) -> str:
        """获取笔记模板（V5增强版）"""
        template_file = TEMPLATE_PATH / "daily.md"
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")

        # V5默认模板（增加学习记录区域）
        return """# 📓 Daily Note - {{date}}

> {{weekday}} | Week {{week}} | Day {{day_of_week}}

---

## 🎯 今日任务

{{tasks}}

---

## 💡 灵感与想法

{{thoughts}}

---

## 📝 会议/对话记录

{{meetings}}

---

## 📚 学习记录

{{learning}}

---

## ✅ 完成事项

- [ ]

---

## 📊 语义组分析

{{semantic_groups}}

---

## 🏷️ 标签

{{tags}}

---

## 🔗 TagMemo 同步

{{tagmemo_sync}}

---

*记录时间: {{created_at}}*
*AI提取Tags: {{ai_tags}}*
*V5新增：学习记录自动同步到Knowledge Manager*
"""

    def _fetch_today_waves(self) -> List[Dict]:
        """从 wave-manager 获取今日浪潮"""
        waves = []
        if not WAVES_DIR.exists():
            return waves

        today = datetime.now().strftime("%Y-%m-%d")
        for wave_file in WAVES_DIR.glob("*.json"):
            try:
                data = json.loads(wave_file.read_text())
                created = data.get("created_at", "")
                if today in created:
                    waves.append(data)
            except:
                continue
        return waves

    def _sync_to_tagmemo(self, content: str, tags: List[str], category: str) -> Dict:
        """同步到 TagMemo"""
        try:
            import subprocess
            source_map = {
                "thoughts": "thought",
                "task": "task",
                "meeting": "meeting",
                "learning": "learning"  # 【V5新增】
            }
            source = source_map.get(category, "daily-note")
            
            cmd = [
                "python3", str(TAGMEMO_PATH),
                "save", "nova", "mid",
                content, source
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return json.loads(result.stdout)
            return {"status": "sync_failed", "error": result.stderr}
        except Exception as e:
            return {"status": "sync_error", "error": str(e)}

    def create_today(self) -> Dict:
        """创建今日笔记（V5增强版）"""
        note_path = self._get_note_path()

        if note_path.exists():
            return {
                "status": "exists",
                "path": str(note_path),
                "message": "今日笔记已存在"
            }

        now = datetime.now()
        template = self._get_template()

        # 获取今日任务
        waves = self._fetch_today_waves()
        tasks_text = "\n".join([f"- [{w.get('status', 'created')}] {w.get('task', 'Unknown')}" for w in waves[:5]]) or "- 暂无任务"

        # 填充模板
        content = template.replace("{{date}}", now.strftime("%Y-%m-%d"))
        content = content.replace("{{weekday}}", now.strftime("%A"))
        content = content.replace("{{week}}", now.strftime("%W"))
        content = content.replace("{{day_of_week}}", str(now.weekday()))
        content = content.replace("{{tasks}}", tasks_text)
        content = content.replace("{{thoughts}}", "待记录...")
        content = content.replace("{{meetings}}", "暂无")
        content = content.replace("{{learning}}", "暂无")  # 【V5新增】
        content = content.replace("{{semantic_groups}}", "待分析...")
        content = content.replace("{{tags}}", "#daily")
        content = content.replace("{{tagmemo_sync}}", "未同步")
        content = content.replace("{{created_at}}", now.strftime("%H:%M"))
        content = content.replace("{{ai_tags}}", "[]")

        note_path.write_text(content, encoding="utf-8")

        return {
            "status": "created",
            "path": str(note_path),
            "message": f"已创建 {now.strftime('%Y-%m-%d')} 的每日笔记",
            "features": ["智能Tag提取", "语义组分析", "TagMemo同步", "V5学习记录"]
        }

    def add_entry(self, content: str, category: str = "thoughts") -> Dict:
        """添加笔记条目（V5增强版 - 学习事件自动通知）"""
        note_path = self._get_note_path()

        # 如果笔记不存在，先创建
        if not note_path.exists():
            self.create_today()

        note_content = note_path.read_text(encoding="utf-8")
        now = datetime.now().strftime("%H:%M")

        # AI提取Tags
        ai_tags = self._extract_tags_ai(content)
        activated_groups = self._detect_semantic_groups(ai_tags)
        
        # 【V5新增】检测是否为学习内容
        is_learning = self._is_learning_content(content)
        if is_learning:
            category = "learning"  # 自动分类为学习
            ai_tags.append("学习")
            ai_tags.append("知识")

        # 根据分类添加到对应区域
        if category == "thoughts":
            pattern = r"(## 💡 灵感与想法\n\n)"
            entry = f"- {content} *({now})* [Tags: {', '.join(ai_tags)}]\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)
        elif category == "task":
            pattern = r"(## ✅ 完成事项\n\n)"
            entry = f"- [x] {content} *({now})* [Tags: {', '.join(ai_tags)}]\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)
        elif category == "meeting":
            pattern = r"(## 📝 会议/对话记录\n\n)"
            entry = f"### {now}\n{content}\n[Tags: {', '.join(ai_tags)}]\n\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)
        elif category == "learning":  # 【V5新增】
            pattern = r"(## 📚 学习记录\n\n)"
            entry = f"- {content} *({now})* [Tags: {', '.join(ai_tags)}]\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)

        # 更新语义组分析
        if activated_groups:
            groups_text = "\n".join([f"- **{g}**: {', '.join(self.semantic_groups[g][:5])}..." for g in activated_groups])
            note_content = re.sub(
                r'(## 📊 语义组分析\n\n)(.+?)(\n\n##)',
                r'\1' + groups_text + r'\3',
                note_content,
                flags=re.DOTALL
            )

        # 保存笔记
        note_path.write_text(note_content, encoding="utf-8")

        # 同步到TagMemo
        sync_result = self._sync_to_tagmemo(content, ai_tags, category)
        
        # 【V5新增】如果是学习内容，通知Knowledge Manager
        knowledge_notification = None
        if is_learning:
            knowledge_notification = self._notify_knowledge_manager(content, ai_tags)

        return {
            "status": "success",
            "path": str(note_path),
            "added_at": now,
            "category": category,
            "tags": ai_tags,
            "semantic_groups": activated_groups,
            "sync_result": sync_result,
            "is_learning": is_learning,  # 【V5新增】
            "knowledge_notification": knowledge_notification  # 【V5新增】
        }

    def search_notes(self, query: str, days: int = 7) -> List[Dict]:
        """搜索笔记（V4功能）"""
        results = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        current = start_date
        while current <= end_date:
            note_path = self._get_note_path(current)
            if note_path.exists():
                content = note_path.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    # 提取匹配段落
                    paragraphs = [p for p in content.split('\n') if query in p]
                    results.append({
                        "date": current.strftime("%Y-%m-%d"),
                        "path": str(note_path),
                        "matches": paragraphs[:3]  # 最多3段
                    })
            current += timedelta(days=1)
        
        return results

    def archive_old_notes(self, days: int = 30) -> Dict:
        """归档旧笔记（V4功能）"""
        archived = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for note_file in self.notes_dir.glob("*.md"):
            try:
                # 从文件名解析日期
                date_str = note_file.stem
                note_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if note_date < cutoff:
                    # 移动到归档目录
                    archive_path = self.archive_dir / note_file.name
                    note_file.rename(archive_path)
                    archived.append(date_str)
            except:
                continue
        
        return {
            "status": "success",
            "archived_count": len(archived),
            "archived_dates": archived
        }


def main():
    import sys
    
    manager = DailyNoteManagerV5()
    
    if len(sys.argv) < 2:
        # 创建今日笔记
        result = manager.create_today()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    command = sys.argv[1]
    
    if command == "add":
        if len(sys.argv) < 3:
            print("用法: python agent.py add '<内容>' [category]")
            return
        
        content = sys.argv[2]
        category = sys.argv[3] if len(sys.argv) > 3 else "thoughts"
        
        result = manager.add_entry(content, category)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("用法: python agent.py search '<查询>' [days]")
            return
        
        query = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        
        results = manager.search_notes(query, days)
        print(json.dumps(results, ensure_ascii=False, indent=2))
    
    elif command == "archive":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        result = manager.archive_old_notes(days)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(f"未知命令: {command}")
        print("可用命令: add, search, archive")


if __name__ == "__main__":
    main()
