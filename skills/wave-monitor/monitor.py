#!/usr/bin/env python3
"""
Wave Monitor - 浪潮监控系统 V1.0
功能：健康检查、超时检测、自动恢复、Agent心跳
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import sys

# 添加事件总线
sys.path.insert(0, str(Path(__file__).parent.parent / "wave-event-bus"))
from bus import emit_event, EventType

class WaveMonitor:
    """浪潮监控系统"""
    
    def __init__(self):
        self.wave_dir = Path.home() / ".openclaw/shared/SYSTEM/waves"
        self.config = {
            "subtask_timeout_minutes": 30,      # 子任务超时时间
            "wave_timeout_hours": 24,           # 浪潮超时时间
            "max_retries": 3,                   # 最大重试次数
            "health_check_interval_minutes": 10 # 健康检查间隔
        }
        self.health_log = Path.home() / ".openclaw/shared/monitor/health.log"
        self.health_log.parent.mkdir(parents=True, exist_ok=True)
    
    def health_check(self) -> Dict:
        """执行健康检查"""
        print("🔍 执行浪潮健康检查...")
        
        issues = []
        fixed = []
        
        # 检查所有浪潮
        for wave_file in self.wave_dir.glob("Wave_*.json"):
            try:
                with open(wave_file, 'r') as f:
                    wave = json.load(f)
                
                wave_id = wave["wave_id"]
                
                # 检查1：超时子任务
                for subtask in wave.get("subtasks", []):
                    if subtask["status"] == "in_progress":
                        issue = self._check_subtask_timeout(wave_id, subtask)
                        if issue:
                            issues.append(issue)
                            # 尝试自动恢复
                            if self._auto_retry_subtask(wave_id, subtask):
                                fixed.append(f"{wave_id}/{subtask['subtask_id']}")
                
                # 检查2：卡住的浪潮
                if wave["status"] == "created" and wave.get("subtasks"):
                    issue = self._check_stuck_wave(wave_id, wave)
                    if issue:
                        issues.append(issue)
                
                # 检查3：Agent负载
                agent_load = self._check_agent_load(wave)
                if agent_load.get("overload"):
                    issues.append({
                        "type": "agent_overload",
                        "wave_id": wave_id,
                        "agent": agent_load["agent"],
                        "task_count": agent_load["task_count"]
                    })
            
            except Exception as e:
                issues.append({
                    "type": "file_error",
                    "file": str(wave_file),
                    "error": str(e)
                })
        
        # 记录健康状态
        self._log_health_status(issues, fixed)
        
        return {
            "status": "completed",
            "checked_at": datetime.now().isoformat(),
            "total_issues": len(issues),
            "auto_fixed": len(fixed),
            "issues": issues,
            "fixed": fixed
        }
    
    def _check_subtask_timeout(self, wave_id: str, subtask: Dict) -> Dict:
        """检查子任务是否超时"""
        started_at = subtask.get("started_at")
        if not started_at:
            return None
        
        try:
            start_time = datetime.fromisoformat(started_at)
            elapsed = datetime.now() - start_time
            
            if elapsed > timedelta(minutes=self.config["subtask_timeout_minutes"]):
                return {
                    "type": "subtask_timeout",
                    "wave_id": wave_id,
                    "subtask_id": subtask["subtask_id"],
                    "agent": subtask["agent"],
                    "elapsed_minutes": elapsed.total_seconds() / 60
                }
        except:
            pass
        
        return None
    
    def _check_stuck_wave(self, wave_id: str, wave: Dict) -> Dict:
        """检查浪潮是否卡住"""
        created_at = wave.get("created_at")
        if not created_at:
            return None
        
        try:
            create_time = datetime.fromisoformat(created_at)
            elapsed = datetime.now() - create_time
            
            # 如果创建了子任务但长时间没有进度
            if elapsed > timedelta(hours=2):
                in_progress = [s for s in wave.get("subtasks", []) if s["status"] == "in_progress"]
                if not in_progress:
                    return {
                        "type": "stuck_wave",
                        "wave_id": wave_id,
                        "elapsed_hours": elapsed.total_seconds() / 3600,
                        "subtasks_count": len(wave.get("subtasks", []))
                    }
        except:
            pass
        
        return None
    
    def _check_agent_load(self, wave: Dict) -> Dict:
        """检查Agent负载"""
        agent_tasks = {}
        
        for subtask in wave.get("subtasks", []):
            agent = subtask["agent"]
            if agent not in agent_tasks:
                agent_tasks[agent] = []
            agent_tasks[agent].append(subtask)
        
        for agent, tasks in agent_tasks.items():
            in_progress = [t for t in tasks if t["status"] == "in_progress"]
            if len(in_progress) >= 3:  # 单个Agent同时执行超过3个任务
                return {
                    "overload": True,
                    "agent": agent,
                    "task_count": len(in_progress)
                }
        
        return {"overload": False}
    
    def _auto_retry_subtask(self, wave_id: str, subtask: Dict) -> bool:
        """自动重试子任务"""
        retry_count = subtask.get("retry_count", 0)
        
        if retry_count >= self.config["max_retries"]:
            # 超过重试次数，标记为失败
            self._fail_subtask(wave_id, subtask["subtask_id"], "超过最大重试次数")
            return False
        
        # 更新重试计数
        wave_file = self.wave_dir / f"{wave_id}.json"
        try:
            with open(wave_file, 'r') as f:
                wave = json.load(f)
            
            for s in wave.get("subtasks", []):
                if s["subtask_id"] == subtask["subtask_id"]:
                    s["retry_count"] = retry_count + 1
                    s["started_at"] = datetime.now().isoformat()  # 重置开始时间
                    break
            
            with open(wave_file, 'w') as f:
                json.dump(wave, f, indent=2)
            
            # 发射重试事件
            emit_event(EventType.SUBTASK_STARTED, wave_id, subtask["agent"], {
                "subtask_id": subtask["subtask_id"],
                "retry": retry_count + 1
            })
            
            return True
        except Exception as e:
            print(f"[Monitor] 重试失败: {e}")
            return False
    
    def _fail_subtask(self, wave_id: str, subtask_id: str, error: str):
        """标记子任务失败"""
        wave_file = self.wave_dir / f"{wave_id}.json"
        try:
            with open(wave_file, 'r') as f:
                wave = json.load(f)
            
            for s in wave.get("subtasks", []):
                if s["subtask_id"] == subtask_id:
                    s["status"] = "failed"
                    s["error"] = error
                    s["completed_at"] = datetime.now().isoformat()
                    break
            
            with open(wave_file, 'w') as f:
                json.dump(wave, f, indent=2)
            
            emit_event(EventType.SUBTASK_FAILED, wave_id, data={
                "subtask_id": subtask_id,
                "error": error
            })
        except Exception as e:
            print(f"[Monitor] 标记失败失败: {e}")
    
    def _log_health_status(self, issues: List[Dict], fixed: List[str]):
        """记录健康状态"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "issues_count": len(issues),
            "fixed_count": len(fixed),
            "issues": issues,
            "fixed": fixed
        }
        
        with open(self.health_log, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    
    def get_system_status(self) -> Dict:
        """获取系统整体状态"""
        waves = list(self.wave_dir.glob("Wave_*.json"))
        
        total = len(waves)
        active = 0
        completed = 0
        failed = 0
        
        agent_stats = {}
        
        for wave_file in waves:
            try:
                with open(wave_file, 'r') as f:
                    wave = json.load(f)
                
                if wave["status"] == "completed":
                    completed += 1
                elif wave["status"] == "failed":
                    failed += 1
                else:
                    active += 1
                
                # Agent统计
                for subtask in wave.get("subtasks", []):
                    agent = subtask["agent"]
                    if agent not in agent_stats:
                        agent_stats[agent] = {"total": 0, "completed": 0, "failed": 0}
                    
                    agent_stats[agent]["total"] += 1
                    if subtask["status"] == "completed":
                        agent_stats[agent]["completed"] += 1
                    elif subtask["status"] == "failed":
                        agent_stats[agent]["failed"] += 1
            
            except:
                continue
        
        return {
            "status": "success",
            "summary": {
                "total_waves": total,
                "active": active,
                "completed": completed,
                "failed": failed,
                "completion_rate": (completed / total * 100) if total > 0 else 0
            },
            "agent_stats": agent_stats,
            "checked_at": datetime.now().isoformat()
        }
    
    def get_recent_health_logs(self, limit: int = 10) -> List[Dict]:
        """获取最近的健康日志"""
        if not self.health_log.exists():
            return []
        
        logs = []
        with open(self.health_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    logs.append(json.loads(line.strip()))
                except:
                    continue
        return logs

def main():
    """命令行入口"""
    import sys
    
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = args.get("action", "check")
    
    monitor = WaveMonitor()
    
    if action == "check":
        result = monitor.health_check()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "status":
        result = monitor.get_system_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "logs":
        result = {"status": "success", "logs": monitor.get_recent_health_logs(args.get("limit", 10))}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(json.dumps({"status": "failed", "message": f"Unknown action: {action}"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
