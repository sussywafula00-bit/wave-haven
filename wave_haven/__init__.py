"""
Wave-Haven Core Package
Multi-Agent Task Orchestration & Knowledge Management System
"""

__version__ = "0.1.0-alpha"
__author__ = "Wave-Haven Contributors"

from .wave import WaveManager, WaveMonitor, EventBus
from .haven import TagMemo, KnowledgeFlow, MemoryOptimizer
from .agents import Nova, Luna, DreamNova, Kiki, Coco

__all__ = [
    'WaveManager',
    'WaveMonitor', 
    'EventBus',
    'TagMemo',
    'KnowledgeFlow',
    'MemoryOptimizer',
    'Nova',
    'Luna',
    'DreamNova',
    'Kiki',
    'Coco',
]
