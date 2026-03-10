#!/usr/bin/env python3
"""
Wave System V3.0 - 综合测试脚本
测试内容：
1. 事件总线
2. 子任务状态流转
3. DreamNova 深度集成
4. 监控系统
5. 知识流自动化
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加技能路径
sys.path.insert(0, str(Path.home() / ".openclaw/workspace_shared/skills/wave-event-bus"))
sys.path.insert(0, str(Path.home() / ".openclaw/workspace_shared/skills/wave-manager"))
sys.path.insert(0, str(Path.home() / ".openclaw/workspace_shared/skills/dream-orchestrator"))
sys.path.insert(0, str(Path.home() / ".openclaw/workspace_shared/skills/wave-monitor"))
sys.path.insert(0, str(Path.home() / ".openclaw/workspace_shared/skills/knowledge-flow"))

from bus import get_event_bus, emit_event, EventType
from agent_v3 import create_wave, assign_task, start_subtask, update_progress, complete_subtask, get_status
from orchestrator import DreamOrchestrator
from monitor import WaveMonitor
from flow import KnowledgeFlow

print("=" * 70)
print("🌊 浪潮系统 V3.0 综合测试")
print("=" * 70)
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

test_results = []

# ============ 测试 1: 事件总线 ============
print("\n【测试 1】事件总线 (Wave Event Bus)")
print("-" * 70)

try:
    bus = get_event_bus()
    
    # 发射测试事件
    emit_event(
        EventType.WAVE_CREATED,
        wave_id="Wave_Test_001",
        data={"task": "测试事件总线", "agents": ["Nova"]}
    )
    
    # 获取最近事件
    events = bus.get_recent_events(5)
    
    if len(events) >= 1:
        print("✅ 事件发射成功")
        print(f"   最近事件数: {len(events)}")
        test_results.append(("事件总线", "通过"))
    else:
        print("⚠️  事件未记录")
        test_results.append(("事件总线", "警告"))
        
except Exception as e:
    print(f"❌ 错误: {e}")
    test_results.append(("事件总线", "失败"))

# ============ 测试 2: 子任务状态流转 ============
print("\n【测试 2】子任务状态流转 (Wave Manager V3)")
print("-" * 70)

try:
    # 创建浪潮
    result = create_wave("测试子任务状态流转")
    wave_id = result["wave_id"]
    print(f"✅ 浪潮创建: {wave_id}")
    
    # 分配子任务
    result = assign_task(wave_id, "Luna", "检索相关记忆")
    subtask_id = result["subtask_id"]
    print(f"✅ 子任务分配: {subtask_id}")
    
    # 开始子任务
    result = start_subtask(wave_id, subtask_id)
    print(f"✅ 子任务开始")
    
    # 更新进度
    result = update_progress(wave_id, subtask_id, 50, "正在检索...")
    print(f"✅ 进度更新: 50%")
    
    # 完成子任务
    result = complete_subtask(wave_id, subtask_id, {"found": "5条记忆"})
    print(f"✅ 子任务完成")
    
    # 查询状态
    status = get_status(wave_id)
    print(f"\n   最终状态:")
    print(f"   - 总子任务: {status['summary']['total']}")
    print(f"   - 已完成: {status['summary']['completed']}")
    print(f"   - 进行中: {status['summary']['in_progress']}")
    
    test_results.append(("子任务状态流转", "通过"))
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("子任务状态流转", "失败"))

# ============ 测试 3: DreamNova 深度集成 ============
print("\n【测试 3】DreamNova 深度集成 (Dream Orchestrator)")
print("-" * 70)

try:
    orchestrator = DreamOrchestrator()
    
    # 测试时段检查
    should, reason = orchestrator.should_use_dream("complex", force=True)
    print(f"✅ 推演判断: {reason}")
    
    # 执行简化版推演（使用模拟数据）
    result = orchestrator.execute_dream_workflow(
        task="测试多阶段推演工作流",
        steps=[
            {"phase": "explore", "iterations": 2},
            {"phase": "evaluate", "iterations": 1, "criteria": ["可行性"]},
            {"phase": "converge", "iterations": 1}
        ],
        force=True
    )
    
    if result["success"]:
        print(f"✅ 推演完成: {result['dream_id']}")
        print(f"   完成阶段: {result['completed_phases']}")
        test_results.append(("DreamNova深度集成", "通过"))
    else:
        print(f"⚠️  推演失败: {result.get('error')}")
        test_results.append(("DreamNova深度集成", "警告"))
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("DreamNova深度集成", "失败"))

# ============ 测试 4: 监控系统 ============
print("\n【测试 4】监控系统 (Wave Monitor)")
print("-" * 70)

try:
    monitor = WaveMonitor()
    
    # 系统状态
    status = monitor.get_system_status()
    print(f"✅ 系统状态获取成功")
    print(f"   总浪潮: {status['summary']['total_waves']}")
    print(f"   活跃: {status['summary']['active']}")
    print(f"   完成率: {status['summary']['completion_rate']:.1f}%")
    
    # 健康检查
    health = monitor.health_check()
    print(f"✅ 健康检查完成")
    print(f"   发现问题: {health['total_issues']}")
    print(f"   自动修复: {health['auto_fixed']}")
    
    test_results.append(("监控系统", "通过"))
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("监控系统", "失败"))

# ============ 测试 5: 知识流自动化 ============
print("\n【测试 5】知识流自动化 (Knowledge Flow)")
print("-" * 70)

try:
    flow = KnowledgeFlow()
    
    # 处理最近的浪潮完成
    wave_dir = Path.home() / ".openclaw/shared/waves"
    recent_waves = sorted(wave_dir.glob("Wave_*.json"), reverse=True)[:1]
    
    if recent_waves:
        wave_file = recent_waves[0]
        wave_id = wave_file.stem
        
        result = flow.process_wave_completion(wave_id)
        
        if result["status"] == "success":
            print(f"✅ 知识沉淀完成: {wave_id}")
            print(f"   关键要点: {result['key_points_count']}")
            print(f"   标签: {', '.join(result['tags'][:5])}")
            test_results.append(("知识流自动化", "通过"))
        else:
            print(f"⚠️  知识沉淀失败: {result.get('message')}")
            test_results.append(("知识流自动化", "警告"))
    else:
        print("⚠️  没有可用的浪潮进行测试")
        test_results.append(("知识流自动化", "跳过"))
    
    # 测试知识统计
    stats = flow.get_knowledge_stats()
    print(f"✅ 知识统计: {stats['total']} 条知识")
    
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    test_results.append(("知识流自动化", "失败"))

# ============ 测试汇总 ============
print("\n" + "=" * 70)
print("📊 测试结果汇总")
print("=" * 70)

passed = sum(1 for _, r in test_results if r == "通过")
failed = sum(1 for _, r in test_results if r == "失败")
warnings = sum(1 for _, r in test_results if r in ["警告", "跳过"])

for name, result in test_results:
    icon = "✅" if result == "通过" else "❌" if result == "失败" else "⚠️"
    print(f"  {icon} {name:20} {result}")

print("-" * 70)
print(f"总计: {passed} 通过, {failed} 失败, {warnings} 警告")
print(f"成功率: {passed/len(test_results)*100:.1f}%")
print("=" * 70)

# 保存测试报告
report = {
    "test_time": datetime.now().isoformat(),
    "results": [{"name": n, "status": r} for n, r in test_results],
    "summary": {
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "total": len(test_results),
        "success_rate": passed/len(test_results)*100
    }
}

report_file = Path.home() / ".openclaw/shared/test_reports/wave_v3_test.json"
report_file.parent.mkdir(parents=True, exist_ok=True)
with open(report_file, 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print(f"\n📄 测试报告已保存: {report_file}")
