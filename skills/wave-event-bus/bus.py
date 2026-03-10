#!/usr/bin/env python3
"""
Wave Event Bus - 浪潮事件总线 V1.0
统一事件通信机制，连接各组件
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class EventType(Enum):
    WAVE_CREATED = "wave_created"
    WAVE_COMPLETED = "wave_completed"
    WAVE_FAILED = "wave_failed"
    SUBTASK_ASSIGNED = "subtask_assigned"
    SUBTASK_STARTED = "subtask_started"
    SUBTASK_PROGRESS = "subtask_progress"
    SUBTASK_COMPLETED = "subtask_completed"
    SUBTASK_FAILED = "subtask_failed"
    AGENT_CALLED = "agent_called"
    AGENT_COMPLETED = "agent_completed"
    KNOWLEDGE_LEARNED = "knowledge_learned"
    DAILY_NOTE_RECORDED = "daily_note_recorded"

@dataclass
class WaveEvent:
    event_type: EventType
    timestamp: str
    wave_id: str = None
    agent: str = None
    data: Dict = None
    
    def to_dict(self):
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "wave_id": self.wave_id,
            "agent": self.agent,
            "data": self.data or {}
        }

class WaveEventBus:
    """浪潮事件总线 - 核心组件"""
    
    def __init__(self):
        self.base_path = Path.home() / ".openclaw/shared/SYSTEM/events"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.log_file = self.base_path / "events.log"
        self.handlers: Dict[EventType, List[Callable]] = {}
        self._init_handlers()
    
    def _init_handlers(self):
        """初始化默认处理器"""
        # 动态导入处理器，避免循环依赖
        self.handlers[EventType.WAVE_CREATED] = [self._on_wave_created]
        self.handlers[EventType.SUBTASK_COMPLETED] = [self._on_subtask_completed]
        self.handlers[EventType.WAVE_COMPLETED] = [self._on_wave_completed]
    
    def emit(self, event: WaveEvent):
        """发射事件"""
        # 记录到日志
        self._log_event(event)
        
        # 调用处理器
        handlers = self.handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                print(f"[EventBus] 处理器错误: {e}")
    
    def _log_event(self, event: WaveEvent):
        """记录事件到日志文件"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')
    
    def _on_wave_created(self, event: WaveEvent):
        """浪潮创建处理器 - 自动记录 DailyNote"""
        try:
            # 动态导入，处理路径问题
            import sys
            from pathlib import Path
            daily_note_path = Path.home() / ".openclaw/agents/nova/workspace/output"
            if str(daily_note_path) not in sys.path:
                sys.path.insert(0, str(daily_note_path))
            from daily_note_v6 import auto_daily_note
            auto_daily_note(
                'task_start',
                f"启动浪潮 {event.wave_id}: {event.data.get('task', '未知任务')}",
                {'wave_id': event.wave_id, 'agents': event.data.get('agents', [])}
            )
        except Exception as e:
            print(f"[EventBus] DailyNote 记录跳过: {e}")
    
    def _on_subtask_completed(self, event: WaveEvent):
        """子任务完成处理器"""
        try:
            from daily_note_v6 import auto_daily_note
            auto_daily_note(
                'task_complete',
                f"子任务完成: {event.data.get('subtask_desc', '')}",
                {
                    'wave_id': event.wave_id,
                    'agent': event.agent,
                    'subtask_id': event.data.get('subtask_id')
                }
            )
        except Exception as e:
            print(f"[EventBus] DailyNote 记录失败: {e}")
    
    def _on_wave_completed(self, event: WaveEvent):
        """浪潮完成处理器 - 触发知识沉淀"""
        try:
            # 触发知识学习
            wave_file = Path.home() / f".openclaw/shared/SYSTEM/waves/{event.wave_id}.json"
            if wave_file.exists():
                self._trigger_knowledge_learning(event.wave_id, wave_file)
            
            # 记录 DailyNote
            from daily_note_v6 import auto_daily_note
            auto_daily_note(
                'milestone',
                f"浪潮完成: {event.wave_id}",
                {'wave_id': event.wave_id, 'result': event.data.get('result', {})}
            )
        except Exception as e:
            print(f"[EventBus] 知识沉淀失败: {e}")
    
    def _trigger_knowledge_learning(self, wave_id: str, wave_file: Path):
        """触发知识学习"""
        try:
            with open(wave_file, 'r') as f:
                wave_data = json.load(f)
            
            # 提取关键信息生成知识摘要
            knowledge_content = f"""
# 浪潮 {wave_id} 知识摘要

任务: {wave_data.get('task', 'N/A')}
Agent: {', '.join(wave_data.get('agents', []))}
子任务数: {len(wave_data.get('subtasks', []))}

## 执行记录
"""
            for subtask in wave_data.get('subtasks', []):
                knowledge_content += f"- [{subtask.get('status')}] {subtask.get('agent')}: {subtask.get('desc')}\n"
            
            # 保存到知识目录
            knowledge_dir = Path.home() / ".openclaw/shared/SYSTEM/knowledge/auto"
            knowledge_dir.mkdir(parents=True, exist_ok=True)
            knowledge_file = knowledge_dir / f"{wave_id}_knowledge.md"
            
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                f.write(knowledge_content)
            
            print(f"[EventBus] 知识已沉淀: {knowledge_file}")
        except Exception as e:
            print(f"[EventBus] 知识学习失败: {e}")
    
    def get_recent_events(self, limit: int = 50) -> List[Dict]:
        """获取最近事件"""
        if not self.log_file.exists():
            return []
        
        events = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    events.append(json.loads(line.strip()))
                except:
                    continue
        return events
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """订阅事件"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

# 全局事件总线实例
_event_bus = None

def get_event_bus() -> WaveEventBus:
    """获取全局事件总线实例"""
    global _event_bus
    if _event_bus is None:
        _event_bus = WaveEventBus()
    return _event_bus

def emit_event(event_type: EventType, wave_id: str = None, agent: str = None, data: Dict = None):
    """便捷函数：发射事件"""
    event = WaveEvent(
        event_type=event_type,
        timestamp=datetime.now().isoformat(),
        wave_id=wave_id,
        agent=agent,
        data=data
    )
    get_event_bus().emit(event)

if __name__ == '__main__':
    # 测试
    print("🌊 Wave Event Bus V1.0 测试")
    
    bus = get_event_bus()
    
    # 测试发射事件
    emit_event(
        EventType.WAVE_CREATED,
        wave_id="Wave_20260306_Test",
        data={"task": "测试事件总线", "agents": ["Nova"]}
    )
    
    print("\n✅ 事件总线测试完成")
    print(f"日志位置: {bus.log_file}")
