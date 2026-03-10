#!/usr/bin/env python3
"""Wave Manager V3.0 - 增强版子任务状态流转
支持：created → assigned → in_progress → completed/failed
新增：事件总线集成、进度追踪
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from enum import Enum

# 添加事件总线到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "wave-event-bus"))
from bus import emit_event, EventType

WAVE_DIR = Path.home() / ".openclaw" / "shared" / "waves"
VERSION_DIR = Path.home() / ".openclaw" / "shared" / "versions"

class SubtaskStatus(Enum):
    CREATED = "created"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

def ensure_dirs():
    WAVE_DIR.mkdir(parents=True, exist_ok=True)
    VERSION_DIR.mkdir(parents=True, exist_ok=True)

def generate_wave_id():
    return f"Wave_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def create_wave(task, creator="Nova"):
    ensure_dirs()
    wave_id = generate_wave_id()
    wave = {
        "wave_id": wave_id,
        "status": "created",
        "task": task,
        "creator": creator,
        "created_at": datetime.now().isoformat(),
        "completed_at": None,
        "agents": [],
        "subtasks": [],
        "logs": [],
        "metadata": {
            "total_subtasks": 0,
            "completed_subtasks": 0,
            "failed_subtasks": 0
        }
    }
    with open(WAVE_DIR / f"{wave_id}.json", "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.WAVE_CREATED, wave_id, data={"task": task, "agents": []})
    
    return {"status": "success", "wave_id": wave_id, "message": f"[Nova] [CreateWave] [{wave_id}] {task}"}

def assign_task(wave_id, agent, subtask):
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    subtask_id = f"{wave_id}_{agent}_{len(wave['subtasks'])}"
    subtask_obj = {
        "subtask_id": subtask_id,
        "agent": agent,
        "desc": subtask,
        "status": SubtaskStatus.ASSIGNED.value,
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "assigned_at": datetime.now().isoformat(),
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None
    }
    
    wave["subtasks"].append(subtask_obj)
    wave["metadata"]["total_subtasks"] = len(wave["subtasks"])
    
    if agent not in wave["agents"]:
        wave["agents"].append(agent)
    
    with open(wave_file, "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.SUBTASK_ASSIGNED, wave_id, agent, 
               {"subtask_id": subtask_id, "subtask_desc": subtask})
    
    return {"status": "success", "subtask_id": subtask_id, 
            "message": f"[Nova] [Assign] → {agent}: {subtask}"}

def start_subtask(wave_id, subtask_id):
    """开始执行子任务"""
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    for subtask in wave["subtasks"]:
        if subtask["subtask_id"] == subtask_id:
            subtask["status"] = SubtaskStatus.IN_PROGRESS.value
            subtask["started_at"] = datetime.now().isoformat()
            break
    
    with open(wave_file, "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.SUBTASK_STARTED, wave_id, data={"subtask_id": subtask_id})
    
    return {"status": "success", "message": f"Subtask {subtask_id} started"}

def update_progress(wave_id, subtask_id, progress, message=None):
    """更新子任务进度 (0-100)"""
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    for subtask in wave["subtasks"]:
        if subtask["subtask_id"] == subtask_id:
            subtask["progress"] = min(100, max(0, progress))
            if message:
                wave["logs"].append({
                    "timestamp": datetime.now().isoformat(),
                    "subtask_id": subtask_id,
                    "message": message
                })
            break
    
    with open(wave_file, "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.SUBTASK_PROGRESS, wave_id, data={
        "subtask_id": subtask_id, 
        "progress": progress,
        "message": message
    })
    
    return {"status": "success", "progress": progress}

def complete_subtask(wave_id, subtask_id, result=None):
    """完成子任务"""
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    subtask_desc = ""
    for subtask in wave["subtasks"]:
        if subtask["subtask_id"] == subtask_id:
            subtask["status"] = SubtaskStatus.COMPLETED.value
            subtask["progress"] = 100
            subtask["completed_at"] = datetime.now().isoformat()
            subtask["result"] = result or {}
            subtask_desc = subtask["desc"]
            break
    
    # 更新统计
    wave["metadata"]["completed_subtasks"] = len([
        s for s in wave["subtasks"] if s["status"] == SubtaskStatus.COMPLETED.value
    ])
    
    # 检查是否全部完成
    if wave["metadata"]["completed_subtasks"] == wave["metadata"]["total_subtasks"]:
        wave["status"] = "completed"
        wave["completed_at"] = datetime.now().isoformat()
    
    with open(wave_file, "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.SUBTASK_COMPLETED, wave_id, data={
        "subtask_id": subtask_id,
        "subtask_desc": subtask_desc,
        "result": result
    })
    
    return {"status": "success", "message": f"Subtask {subtask_id} completed"}

def fail_subtask(wave_id, subtask_id, error_message):
    """标记子任务失败"""
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    for subtask in wave["subtasks"]:
        if subtask["subtask_id"] == subtask_id:
            subtask["status"] = SubtaskStatus.FAILED.value
            subtask["error"] = error_message
            subtask["completed_at"] = datetime.now().isoformat()
            break
    
    # 更新统计
    wave["metadata"]["failed_subtasks"] = len([
        s for s in wave["subtasks"] if s["status"] == SubtaskStatus.FAILED.value
    ])
    
    with open(wave_file, "w") as f:
        json.dump(wave, f, indent=2)
    
    # 发射事件
    emit_event(EventType.SUBTASK_FAILED, wave_id, data={
        "subtask_id": subtask_id,
        "error": error_message
    })
    
    return {"status": "success", "message": f"Subtask {subtask_id} marked as failed"}

def get_status(wave_id):
    wave_file = WAVE_DIR / f"{wave_id}.json"
    if not wave_file.exists():
        return {"status": "failed", "message": f"Wave {wave_id} not found"}
    
    with open(wave_file) as f:
        wave = json.load(f)
    
    total = len(wave["subtasks"])
    completed = len([s for s in wave["subtasks"] if s["status"] == SubtaskStatus.COMPLETED.value])
    in_progress = len([s for s in wave["subtasks"] if s["status"] == SubtaskStatus.IN_PROGRESS.value])
    failed = len([s for s in wave["subtasks"] if s["status"] == SubtaskStatus.FAILED.value])
    
    progress = (completed / total * 100) if total > 0 else 0
    
    return {
        "status": "success",
        "wave": wave,
        "progress": progress,
        "summary": {
            "total": total,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "pending": total - completed - in_progress - failed
        }
    }

def list_waves(status_filter=None):
    """列出所有浪潮"""
    ensure_dirs()
    waves = []
    
    for wave_file in WAVE_DIR.glob("Wave_*.json"):
        try:
            with open(wave_file) as f:
                wave = json.load(f)
                if status_filter is None or wave.get("status") == status_filter:
                    waves.append({
                        "wave_id": wave["wave_id"],
                        "status": wave["status"],
                        "task": wave["task"],
                        "agents": wave.get("agents", []),
                        "progress": len([s for s in wave.get("subtasks", []) 
                                       if s.get("status") == "completed"]) / len(wave.get("subtasks", [1])) * 100
                    })
        except:
            continue
    
    return sorted(waves, key=lambda x: x["wave_id"], reverse=True)

def save_version(version, rules):
    ensure_dirs()
    version_data = {
        "version": version,
        "rules": rules,
        "saved_at": datetime.now().isoformat()
    }
    with open(VERSION_DIR / f"{version}.json", "w") as f:
        json.dump(version_data, f, indent=2)
    with open(VERSION_DIR / "current.json", "w") as f:
        json.dump(version_data, f, indent=2)
    return {"status": "success", "message": f"[Kiki] [VersionSaved] [{version}]"}

def rollback(target_version):
    version_file = VERSION_DIR / f"{target_version}.json"
    if not version_file.exists():
        return {"status": "failed", "message": f"Version {target_version} not found"}
    with open(version_file) as f:
        version_data = json.load(f)
    with open(VERSION_DIR / "current.json", "w") as f:
        json.dump(version_data, f, indent=2)
    return {"status": "success", "version": target_version, "rules": version_data["rules"]}

def main():
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = args.get("action")
    
    handlers = {
        "create": lambda: create_wave(args.get("task")),
        "assign": lambda: assign_task(args.get("wave_id"), args.get("agent"), args.get("subtask")),
        "start": lambda: start_subtask(args.get("wave_id"), args.get("subtask_id")),
        "progress": lambda: update_progress(args.get("wave_id"), args.get("subtask_id"), 
                                           args.get("progress"), args.get("message")),
        "complete": lambda: complete_subtask(args.get("wave_id"), args.get("subtask_id"), 
                                            args.get("result")),
        "fail": lambda: fail_subtask(args.get("wave_id"), args.get("subtask_id"), 
                                     args.get("error")),
        "status": lambda: get_status(args.get("wave_id")),
        "list": lambda: {"status": "success", "waves": list_waves(args.get("status"))},
        "save_version": lambda: save_version(args.get("version"), args.get("rules", {})),
        "rollback": lambda: rollback(args.get("target_version"))
    }
    
    result = handlers.get(action, lambda: {"status": "failed", "message": f"Unknown: {action}"})()
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
