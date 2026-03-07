#!/usr/bin/env python3
"""
Wave Model - Wave任务数据模型
Version: 1.0.0
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Any

class WaveStatus(Enum):
    """Wave状态"""
    PENDING = "pending"      # 🟡 待处理
    RUNNING = "running"      # 🟢 进行中
    COMPLETED = "completed"  # ✅ 已完成
    FAILED = "failed"        # 🔴 失败
    CANCELLED = "cancelled"  # ⚪ 已取消

class WavePriority(Enum):
    """Wave优先级"""
    LOW = "low"      # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"    # 高
    URGENT = "urgent"  # 紧急

class Wave:
    """Wave任务模型"""
    
    def __init__(
        self,
        name: str,
        description: str = "",
        agents: List[str] = None,
        priority: WavePriority = WavePriority.MEDIUM,
        deadline: Optional[datetime] = None,
        metadata: Dict[str, Any] = None
    ):
        self.id = self._generate_id()
        self.name = name
        self.description = description
        self.agents = agents or []
        self.priority = priority
        self.status = WaveStatus.PENDING
        self.progress = 0.0  # 0-100
        self.deadline = deadline
        self.metadata = metadata or {}
        
        # 时间戳
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        
        # 事件日志
        self.events = []
        self._add_event("Wave created", "system")
    
    def _generate_id(self) -> str:
        """生成Wave ID"""
        return f"W{datetime.now().strftime('%y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
    
    def _add_event(self, message: str, agent: str = "system"):
        """添加事件日志"""
        self.events.append({
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message": message
        })
    
    def start(self):
        """开始Wave"""
        if self.status == WaveStatus.PENDING:
            self.status = WaveStatus.RUNNING
            self.started_at = datetime.now()
            self._add_event("Wave started")
    
    def update_progress(self, progress: float, agent: str = "system"):
        """更新进度"""
        self.progress = max(0.0, min(100.0, progress))
        if self.progress > 0 and self.status == WaveStatus.PENDING:
            self.start()
        self._add_event(f"Progress updated to {progress}%", agent)
    
    def complete(self, success: bool = True):
        """完成Wave"""
        if success:
            self.status = WaveStatus.COMPLETED
            self.progress = 100.0
        else:
            self.status = WaveStatus.FAILED
        self.completed_at = datetime.now()
        self._add_event(f"Wave {'completed' if success else 'failed'}")
    
    def cancel(self):
        """取消Wave"""
        if self.status in [WaveStatus.PENDING, WaveStatus.RUNNING]:
            self.status = WaveStatus.CANCELLED
            self.completed_at = datetime.now()
            self._add_event("Wave cancelled")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "agents": self.agents,
            "priority": self.priority.value,
            "status": self.status.value,
            "progress": self.progress,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "events": self.events
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Wave':
        """从字典创建"""
        wave = cls.__new__(cls)
        wave.id = data.get("id", "")
        wave.name = data.get("name", "")
        wave.description = data.get("description", "")
        wave.agents = data.get("agents", [])
        wave.priority = WavePriority(data.get("priority", "medium"))
        wave.status = WaveStatus(data.get("status", "pending"))
        wave.progress = data.get("progress", 0.0)
        wave.metadata = data.get("metadata", {})
        wave.events = data.get("events", [])
        
        # 解析时间
        if data.get("deadline"):
            wave.deadline = datetime.fromisoformat(data["deadline"])
        else:
            wave.deadline = None
        
        wave.created_at = datetime.fromisoformat(data["created_at"])
        wave.started_at = datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None
        wave.completed_at = datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None
        
        return wave
    
    def get_status_icon(self) -> str:
        """获取状态图标"""
        icons = {
            WaveStatus.PENDING: "🟡",
            WaveStatus.RUNNING: "🔵",
            WaveStatus.COMPLETED: "✅",
            WaveStatus.FAILED: "🔴",
            WaveStatus.CANCELLED: "⚪"
        }
        return icons.get(self.status, "❓")
    
    def get_priority_icon(self) -> str:
        """获取优先级图标"""
        icons = {
            WavePriority.LOW: "🔵",
            WavePriority.MEDIUM: "🟢",
            WavePriority.HIGH: "🟠",
            WavePriority.URGENT: "🔴"
        }
        return icons.get(self.priority, "⚪")
    
    def is_overdue(self) -> bool:
        """检查是否逾期"""
        if self.deadline and self.status in [WaveStatus.PENDING, WaveStatus.RUNNING]:
            return datetime.now() > self.deadline
        return False
    
    def get_duration(self) -> Optional[timedelta]:
        """获取持续时间"""
        if self.started_at:
            end = self.completed_at or datetime.now()
            return end - self.started_at
        return None
    
    def __str__(self) -> str:
        return f"{self.get_status_icon()} {self.id}: {self.name} ({self.progress:.0f}%)"


class WaveManager:
    """Wave管理器"""
    
    def __init__(self, storage_dir: Path = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".openclaw/shared/SYSTEM/waves"
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.waves: Dict[str, Wave] = {}
        self._load_waves()
    
    def _get_wave_path(self, wave_id: str) -> Path:
        """获取Wave文件路径"""
        return self.storage_dir / f"{wave_id}.json"
    
    def _load_waves(self):
        """加载所有Wave"""
        for wave_file in self.storage_dir.glob("*.json"):
            try:
                with open(wave_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    wave = Wave.from_dict(data)
                    self.waves[wave.id] = wave
            except Exception as e:
                print(f"Warning: Failed to load {wave_file}: {e}")
    
    def create_wave(
        self,
        name: str,
        description: str = "",
        agents: List[str] = None,
        priority: str = "medium",
        deadline: Optional[datetime] = None
    ) -> Wave:
        """创建新Wave"""
        priority_enum = WavePriority(priority.lower())
        wave = Wave(
            name=name,
            description=description,
            agents=agents,
            priority=priority_enum,
            deadline=deadline
        )
        self.waves[wave.id] = wave
        self._save_wave(wave)
        return wave
    
    def get_wave(self, wave_id: str) -> Optional[Wave]:
        """获取Wave"""
        return self.waves.get(wave_id)
    
    def list_waves(
        self,
        status: Optional[WaveStatus] = None,
        agent: Optional[str] = None,
        limit: int = 100
    ) -> List[Wave]:
        """列出Waves"""
        waves = list(self.waves.values())
        
        # 过滤
        if status:
            waves = [w for w in waves if w.status == status]
        if agent:
            waves = [w for w in waves if agent in w.agents]
        
        # 排序：按创建时间倒序
        waves.sort(key=lambda w: w.created_at, reverse=True)
        
        return waves[:limit]
    
    def update_wave(self, wave: Wave):
        """更新Wave"""
        self.waves[wave.id] = wave
        self._save_wave(wave)
    
    def _save_wave(self, wave: Wave):
        """保存Wave到文件"""
        wave_path = self._get_wave_path(wave.id)
        with open(wave_path, 'w', encoding='utf-8') as f:
            json.dump(wave.to_dict(), f, indent=2, ensure_ascii=False)
    
    def delete_wave(self, wave_id: str) -> bool:
        """删除Wave"""
        if wave_id in self.waves:
            wave_path = self._get_wave_path(wave_id)
            if wave_path.exists():
                wave_path.unlink()
            del self.waves[wave_id]
            return True
        return False
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        stats = {
            "total": len(self.waves),
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }
        for wave in self.waves.values():
            stats[wave.status.value] += 1
        return stats


if __name__ == "__main__":
    # 测试
    manager = WaveManager()
    
    # 创建测试Wave
    wave = manager.create_wave(
        name="测试任务",
        description="这是一个测试任务",
        agents=["nova", "luna"],
        priority="high"
    )
    print(f"Created: {wave}")
    
    # 更新进度
    wave.start()
    wave.update_progress(50, "nova")
    manager.update_wave(wave)
    
    # 列出所有
    print("\nAll waves:")
    for w in manager.list_waves():
        print(f"  {w}")
