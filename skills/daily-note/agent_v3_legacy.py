#!/usr/bin/env python3
"""
DailyNote - 每日笔记管理 Skill
自动化的日记系统，支持任务追踪、灵感记录、周回顾
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

# 确保目录存在
NOTES_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)


class DailyNoteManager:
    """每日笔记管理器"""

    def __init__(self):
        self.notes_dir = NOTES_DIR
        self.archive_dir = ARCHIVE_DIR

    def _get_note_path(self, date: Optional[datetime] = None) -> Path:
        """获取指定日期的笔记路径"""
        if date is None:
            date = datetime.now()
        filename = date.strftime("%Y-%m-%d.md")
        return self.notes_dir / filename

    def _get_template(self) -> str:
        """获取笔记模板"""
        template_file = TEMPLATE_PATH / "daily.md"
        if template_file.exists():
            return template_file.read_text(encoding="utf-8")

        # 默认模板
        return """# 📓 Daily Note - {{date}}

> {{weekday}} | Week {{week}}

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

## 📌 明日待办

{{tomorrow_tasks}}

---

## 🏷️ 标签

{{tags}}

---

*记录时间: {{created_at}}*
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

    def create_today(self) -> Dict:
        """创建今日笔记"""
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
        content = content.replace("{{tasks}}", tasks_text)
        content = content.replace("{{thoughts}}", "待记录...")
        content = content.replace("{{meetings}}", "暂无")
        content = content.replace("{{tomorrow_tasks}}", "- 待规划")
        content = content.replace("{{tags}}", "#daily")
        content = content.replace("{{created_at}}", now.strftime("%H:%M"))

        note_path.write_text(content, encoding="utf-8")

        return {
            "status": "created",
            "path": str(note_path),
            "message": f"已创建 {now.strftime('%Y-%m-%d')} 的每日笔记"
        }

    def add_entry(self, content: str, category: str = "thoughts") -> Dict:
        """添加笔记条目"""
        note_path = self._get_note_path()

        # 如果笔记不存在，先创建
        if not note_path.exists():
            self.create_today()

        note_content = note_path.read_text(encoding="utf-8")
        now = datetime.now().strftime("%H:%M")

        # 根据分类添加到对应区域
        if category == "thoughts":
            # 添加到灵感区域
            pattern = r"(## 💡 灵感与想法\n\n)"
            entry = f"- {content} *({now})*\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)
        elif category == "task":
            # 添加到完成事项
            pattern = r"(## ✅ 完成事项\n\n)"
            entry = f"- [x] {content} *({now})*\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)
        elif category == "meeting":
            # 添加到会议记录
            pattern = r"(## 📝 会议/对话记录\n\n)"
            entry = f"### {now}\n{content}\n\n"
            note_content = re.sub(pattern, r"\1" + entry, note_content)

        # 提取标签
        tags = re.findall(r'#(\w+)', content)
        if tags:
            tags_section = " ".join([f"#{t}" for t in tags])
            note_content = re.sub(r'(## 🏷️ 标签\n\n)(.+)', r'\1' + tags_section, note_content)

        note_path.write_text(note_content, encoding="utf-8")

        return {
            "status": "added",
            "path": str(note_path),
            "category": category,
            "message": f"已记录到 {category}: {content[:50]}..."
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
        return {
            "status": "success",
            "path": str(note_path),
            "content": content,
            "date": datetime.now().strftime("%Y-%m-%d")
        }

    def view_week(self) -> Dict:
        """查看本周所有笔记"""
        week_notes = []
        today = datetime.now()

        # 获取本周一到周日
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

    def generate_review(self) -> Dict:
        """生成本周回顾报告"""
        week_data = self.view_week()
        notes = week_data.get("notes", [])

        if not notes:
            return {
                "status": "no_data",
                "message": "本周没有笔记记录"
            }

        # 统计信息
        review_content = f"""# 📊 周回顾报告

> Week {week_data['week']} | 共 {len(notes)} 天有记录

---

## 📈 本周概览

- 记录天数: {len(notes)}/7
- 平均每日条目: ~{len(notes) * 3 // max(len(notes), 1)} 条

---

## 📝 笔记列表

"""
        for note in notes:
            review_content += f"### {note['weekday']} ({note['date']})\n"
            review_content += f"{note['preview'][:100]}...\n\n"

        review_content += """---

## 🔑 关键主题

(基于标签自动提取)

"""

        # 保存回顾报告
        review_path = self.archive_dir / f"review-week-{week_data['week']}.md"
        review_path.write_text(review_content, encoding="utf-8")

        return {
            "status": "generated",
            "path": str(review_path),
            "week": week_data['week'],
            "content": review_content
        }

    def search(self, keyword: str) -> Dict:
        """搜索笔记"""
        results = []

        for note_file in self.notes_dir.glob("*.md"):
            content = note_file.read_text(encoding="utf-8")
            if keyword.lower() in content.lower():
                # 找到关键词周围上下文
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines):
                    if keyword.lower() in line.lower():
                        context = '\n'.join(lines[max(0, i-1):min(len(lines), i+2)])
                        matches.append(context)

                results.append({
                    "date": note_file.stem,
                    "path": str(note_file),
                    "matches": matches[:3]  # 最多返回3处匹配
                })

        return {
            "status": "success",
            "keyword": keyword,
            "total_matches": len(results),
            "results": results
        }


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="DailyNote 每日笔记管理")
    parser.add_argument("--today", action="store_true", help="创建今日笔记")
    parser.add_argument("--add", type=str, help="添加笔记条目")
    parser.add_argument("--category", type=str, default="thoughts",
                        choices=["thoughts", "task", "meeting"],
                        help="条目分类")
    parser.add_argument("--view", action="store_true", help="查看今日笔记")
    parser.add_argument("--week", action="store_true", help="查看本周笔记")
    parser.add_argument("--review", action="store_true", help="生成周回顾")
    parser.add_argument("--search", type=str, help="搜索笔记")

    args = parser.parse_args()

    manager = DailyNoteManager()

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
    elif args.review:
        result = manager.generate_review()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif args.search:
        result = manager.search(args.search)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 默认创建今日笔记
        result = manager.create_today()
        print(json.dumps(result, indent=2, ensure_ascii=False))
