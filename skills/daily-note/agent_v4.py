#!/usr/bin/env python3
"""
DailyNote V4.0 - 增强版
集成 TagMemo V4: 智能Tag补全、语义组、时间维度
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

# 确保目录存在
NOTES_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


class DailyNoteManagerV4:
    """每日笔记管理器 V4 - 集成TagMemo"""

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

    def _get_note_path(self, date: Optional[datetime] = None) -> Path:
        """获取指定日期的笔记路径"""
        if date is None:
            date = datetime.now()
        filename = date.strftime("%Y-%m-%d.md")
        return self.notes_dir / filename

    def _get_template(self) -> str:
        """获取笔记模板（V4增强版）"""
        template_file = TEMPLATE_PATH / "daily.md"
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")

        # V4默认模板（增加语义组区域）
        return """# 📓 Daily Note - {{date}}

> {{weekday}} | Week {{week}} | Day {{day_of_week}}

---

## 🎯 今日任务

{{tasks}}

---

## 💡 灵感与想法

- {{thoughts}}

---

## 📝 会议/对话记录

{{meetings}}

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
                "meeting": "meeting"
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
        """创建今日笔记（V4增强版）"""
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
            "features": ["智能Tag提取", "语义组分析", "TagMemo同步"]
        }

    def add_entry(self, content: str, category: str = "thoughts") -> Dict:
        """添加笔记条目（V4增强版 - 自动TagMemo同步）"""
        note_path = self._get_note_path()

        # 如果笔记不存在，先创建
        if not note_path.exists():
            self.create_today()

        note_content = note_path.read_text(encoding="utf-8")
        now = datetime.now().strftime("%H:%M")

        # AI提取Tags
        ai_tags = self._extract_tags_ai(content)
        activated_groups = self._detect_semantic_groups(ai_tags)

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

        # 更新语义组分析
        if activated_groups:
            groups_text = "\n".join([f"- **{g}**: {', '.join(self.semantic_groups[g][:5])}..." for g in activated_groups])
            note_content = re.sub(
                r'(## 📊 语义组分析\n\n)(.+?)(\n\n##)',
                r'\1' + groups_text + r'\3',
                note_content,
                flags=re.DOTALL
            )

        # 更新标签区域
        all_tags = re.findall(r'#(\w+)', note_content)
        all_tags.extend(ai_tags)
        tags_section = " ".join([f"#{t}" for t in set(all_tags)])
        note_content = re.sub(r'(## 🏷️ 标签\n\n)(.+)', r'\1' + tags_section, note_content)

        # 更新AI Tags记录
        note_content = re.sub(r'\*AI提取Tags: .+\*', f'*AI提取Tags: {ai_tags}*', note_content)

        note_path.write_text(note_content, encoding="utf-8")

        # 同步到 TagMemo
        sync_result = self._sync_to_tagmemo(content, ai_tags, category)

        return {
            "status": "added",
            "path": str(note_path),
            "category": category,
            "ai_tags": ai_tags,
            "activated_groups": activated_groups,
            "tagmemo_sync": sync_result.get("status", "unknown"),
            "message": f"已记录并同步: {content[:50]}..."
        }

    def search_by_time(self, time_expression: str) -> Dict:
        """时间感知搜索（V4新功能）"""
        results = []
        
        # 解析时间表达式
        now = datetime.now()
        start_date = None
        end_date = None
        
        if "上周" in time_expression:
            start_date = now - timedelta(days=now.weekday() + 7)
            end_date = start_date + timedelta(days=7)
        elif "最近" in time_expression:
            start_date = now - timedelta(days=7)
            end_date = now
        elif "@7d" in time_expression:
            start_date = now - timedelta(days=7)
            end_date = now
        
        if start_date and end_date:
            current = start_date
            while current <= end_date:
                note_path = self._get_note_path(current)
                if note_path.exists():
                    content = note_path.read_text(encoding="utf-8")
                    results.append({
                        "date": current.strftime("%Y-%m-%d"),
                        "content": content[:500] + "..." if len(content) > 500 else content
                    })
                current += timedelta(days=1)
        
        return {
            "status": "success",
            "time_expression": time_expression,
            "range": f"{start_date.strftime('%Y-%m-%d') if start_date else 'N/A'} ~ {end_date.strftime('%Y-%m-%d') if end_date else 'N/A'}",
            "results": results,
            "count": len(results)
        }

    def view_today(self) -> Dict:
        """查看今日笔记"""
        note_path = self._get_note_path()

        if not note_path.exists():
            return {
                "status": "not_found",
                "message": "今日笔记不存在，请先创建"
            }

        content = note_path.read_text(encoding="utf-8")
        
        # 提取AI Tags统计
        ai_tags_match = re.search(r'AI提取Tags: (\[.+\])', content)
        ai_tags = json.loads(ai_tags_match.group(1)) if ai_tags_match else []

        return {
            "status": "success",
            "path": str(note_path),
            "content": content,
            "ai_tags_count": len(ai_tags),
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    def view_week(self) -> Dict:
        """查看本周所有笔记"""
        week_notes = []
        today = datetime.now()

        monday = today - timedelta(days=today.weekday())
        for i in range(7):
            date = monday + timedelta(days=i)
            note_path = self._get_note_path(date)
            if note_path.exists():
                content = note_path.read_text(encoding="utf-8")
                week_notes.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "weekday": date.strftime("%a"),
                    "path": str(note_path),
                    "preview": content[:200] + "..." if len(content) > 200 else content
                })

        return {
            "status": "success",
            "week": today.strftime("%W"),
            "notes_count": len(week_notes),
            "notes": week_notes
        }

    def search(self, keyword: str, use_semantic: bool = False) -> Dict:
        """搜索笔记（V4增强 - 支持语义组）"""
        results = []
        
        # 语义组扩展
        search_terms = [keyword]
        if use_semantic:
            for group_name, group_tags in self.semantic_groups.items():
                if keyword in group_tags or keyword == group_name:
                    search_terms.extend(group_tags[:3])

        for note_file in self.notes_dir.glob("*.md"):
            content = note_file.read_text(encoding="utf-8")
            
            # 检查所有搜索词
            matched = any(term.lower() in content.lower() for term in search_terms)
            
            if matched:
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines):
                    if any(term.lower() in line.lower() for term in search_terms):
                        context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                        matches.append(context)

                results.append({
                    "date": note_file.stem,
                    "path": str(note_file),
                    "matches": matches[:3]
                })

        return {
            "status": "success",
            "keyword": keyword,
            "search_terms": search_terms if use_semantic else [keyword],
            "total_matches": len(results),
            "results": results
        }


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DailyNote V4.0 - 增强版")
    parser.add_argument("--today", action="store_true", help="创建今日笔记")
    parser.add_argument("--add", type=str, help="添加笔记条目")
    parser.add_argument("--category", type=str, default="thoughts",
                        choices=["thoughts", "task", "meeting"],
                        help="条目分类")
    parser.add_argument("--view", action="store_true", help="查看今日笔记")
    parser.add_argument("--week", action="store_true", help="查看本周笔记")
    parser.add_argument("--search", type=str, help="搜索笔记")
    parser.add_argument("--semantic", action="store_true", help="启用语义组搜索")
    parser.add_argument("--time-search", type=str, help="时间感知搜索（如：上周、最近、@7d）")

    args = parser.parse_args()

    manager = DailyNoteManagerV4()

    if args.today:
        result = manager.create_today()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.add:
        result = manager.add_entry(args.add, args.category)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.view:
        result = manager.view_today()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.week:
        result = manager.view_week()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.search:
        result = manager.search(args.search, args.semantic)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.time_search:
        result = manager.search_by_time(args.time_search)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        result = manager.create_today()
        print(json.dumps(result, indent=2, ensure_ascii=False))
