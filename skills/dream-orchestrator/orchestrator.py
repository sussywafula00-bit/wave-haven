#!/usr/bin/env python3
"""
Dream Orchestrator - 梦境推演编排器 V1.0
深度集成 DreamNova，支持多阶段推演工作流
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import Dict, List

# 添加事件总线
sys.path.insert(0, str(Path(__file__).parent.parent / "wave-event-bus"))
from bus import emit_event, EventType

class DreamPhase(Enum):
    EXPLORE = "explore"       # 探索阶段
    EVALUATE = "evaluate"     # 评估阶段
    CONVERGE = "converge"     # 收敛阶段

class DreamOrchestrator:
    """梦境推演编排器"""
    
    def __init__(self):
        self.base_path = Path.home() / ".openclaw/shared/SYSTEM/dreams"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.dreamnova_script = Path.home() / ".openclaw/agents/dreamnova/workspace/skills/dream-engine/agent.py"
    
    def is_dream_window(self, start="02:00", end="04:00") -> bool:
        """检查是否在梦境时段"""
        from datetime import time as dt_time
        now = datetime.now().time()
        s = datetime.strptime(start, "%H:%M").time()
        e = datetime.strptime(end, "%H:%M").time()
        return s <= now <= e
    
    def should_use_dream(self, complexity: str, force: bool = False) -> tuple:
        """判断是否需要梦境推演"""
        if complexity == "simple":
            return False, "简单任务，跳过梦境"
        if not force and not self.is_dream_window():
            return False, "非梦境时段（02:00-04:00），建议定时执行或用 force"
        return True, "需要梦境推演"
    
    def execute_dream_workflow(self, task: str, steps: List[Dict], 
                               wave_id: str = None, force: bool = False) -> Dict:
        """执行梦境推演工作流"""
        
        dream_id = f"Dream_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 创建梦境记录
        dream_record = {
            "dream_id": dream_id,
            "wave_id": wave_id,
            "task": task,
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "phases": [],
            "final_output": None,
            "status": "running"
        }
        
        print(f"\n🌙 启动梦境推演: {dream_id}")
        print(f"   任务: {task}")
        print(f"   阶段数: {len(steps)}")
        
        context = ""
        
        for i, step in enumerate(steps, 1):
            phase = step.get("phase", "explore")
            iterations = step.get("iterations", 1)
            
            print(f"\n【阶段 {i}/{len(steps)}】{phase.upper()}")
            print("-" * 60)
            
            phase_result = self._execute_phase(
                dream_id=dream_id,
                phase=phase,
                task=task,
                context=context,
                iterations=iterations,
                criteria=step.get("criteria", [])
            )
            
            dream_record["phases"].append(phase_result)
            
            if not phase_result["success"]:
                dream_record["status"] = "failed"
                dream_record["error"] = phase_result.get("error", "Unknown error")
                self._save_dream_record(dream_record)
                return {
                    "success": False,
                    "dream_id": dream_id,
                    "error": phase_result.get("error"),
                    "completed_phases": i - 1
                }
            
            # 更新上下文
            context += f"\n\n【{phase.upper()} 阶段输出】\n{phase_result['output']}"
            
            print(f"   ✅ 阶段完成")
        
        # 完成
        dream_record["status"] = "completed"
        dream_record["completed_at"] = datetime.now().isoformat()
        dream_record["final_output"] = context
        self._save_dream_record(dream_record)
        
        # 发射事件
        if wave_id:
            emit_event(EventType.WAVE_COMPLETED, wave_id, data={
                "dream_id": dream_id,
                "result": context
            })
        
        print(f"\n🌟 梦境推演完成: {dream_id}")
        
        return {
            "success": True,
            "dream_id": dream_id,
            "wave_id": wave_id,
            "completed_phases": len(steps),
            "output": context,
            "record_file": str(self.base_path / f"{dream_id}.json")
        }
    
    def _execute_phase(self, dream_id: str, phase: str, task: str, 
                       context: str, iterations: int, criteria: List) -> Dict:
        """执行单个推演阶段"""
        
        # 构建阶段提示
        phase_prompts = {
            "explore": f"""
【探索阶段】对以下任务进行多角度探索分析：

任务: {task}

要求：
1. 列出至少3种不同的解决思路
2. 每种思路的优缺点
3. 潜在的风险和机会
4. 不要急于下结论，充分发散

{context}

请提供结构化的探索分析：
""",
            "evaluate": f"""
【评估阶段】基于以上探索结果进行评估：

评估标准: {', '.join(criteria) if criteria else '可行性、风险、收益'}

要求：
1. 对每个方案进行量化评分（1-10分）
2. 识别各方案的关键假设
3. 评估失败模式和应对策略
4. 给出明确的优劣排序

上下文：
{context}

请提供结构化的评估报告：
""",
            "converge": f"""
【收敛阶段】综合以上分析给出最终建议：

要求：
1. 推荐最优方案并说明理由
2. 提供具体的执行步骤
3. 列出关键里程碑
4. 明确成功指标

上下文：
{context}

请提供结构化的最终报告：
"""
        }
        
        prompt = phase_prompts.get(phase, phase_prompts["explore"])
        
        # 模拟 DreamNova 调用（实际集成时调用 agent-coordinator）
        # 这里使用简化版本地推演
        output = self._simulate_dreamnova(prompt, iterations)
        
        return {
            "phase": phase,
            "success": True,
            "output": output,
            "iterations": iterations,
            "timestamp": datetime.now().isoformat()
        }
    
    def _simulate_dreamnova(self, prompt: str, iterations: int) -> str:
        """模拟 DreamNova 推演（实际部署时替换为真实调用）"""
        # 简化的推演输出
        return f"""
[DreamNova 推演输出 - {iterations} 轮迭代]

基于深度分析，得出以下结论：
1. 方案A具有最高可行性，建议优先采用
2. 关键风险点已识别并制定应对策略
3. 预期收益符合目标要求
4. 执行路径清晰，可立即启动

详细分析内容将随实际 DreamNova 集成而增强。
"""
    
    def _save_dream_record(self, record: Dict):
        """保存梦境记录"""
        file_path = self.base_path / f"{record['dream_id']}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(record, f, indent=2, ensure_ascii=False)
    
    def get_dream_status(self, dream_id: str) -> Dict:
        """获取梦境状态"""
        file_path = self.base_path / f"{dream_id}.json"
        if not file_path.exists():
            return {"status": "failed", "message": f"Dream {dream_id} not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return {"status": "success", "dream": json.load(f)}
    
    def list_dreams(self, limit: int = 20) -> List[Dict]:
        """列出最近的梦境"""
        dreams = []
        for file_path in sorted(self.base_path.glob("Dream_*.json"), reverse=True)[:limit]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    dream = json.load(f)
                    dreams.append({
                        "dream_id": dream["dream_id"],
                        "status": dream["status"],
                        "task": dream["task"][:50] + "..." if len(dream["task"]) > 50 else dream["task"],
                        "created_at": dream["created_at"],
                        "phases_count": len(dream.get("phases", []))
                    })
            except:
                continue
        return dreams

def main():
    """命令行入口"""
    args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    action = args.get("action")
    
    orchestrator = DreamOrchestrator()
    
    if action == "advise":
        should, reason = orchestrator.should_use_dream(
            args.get("complexity", "normal"),
            args.get("force", False)
        )
        print(json.dumps({"should_dream": should, "reason": reason}, ensure_ascii=False))
    
    elif action == "execute":
        result = orchestrator.execute_dream_workflow(
            task=args.get("task"),
            steps=args.get("steps", [
                {"phase": "explore", "iterations": 3},
                {"phase": "evaluate", "iterations": 2, "criteria": ["可行性", "风险", "收益"]},
                {"phase": "converge", "iterations": 1}
            ]),
            wave_id=args.get("wave_id"),
            force=args.get("force", False)
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "status":
        result = orchestrator.get_dream_status(args.get("dream_id"))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif action == "list":
        result = {"status": "success", "dreams": orchestrator.list_dreams(args.get("limit", 20))}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    else:
        print(json.dumps({"status": "failed", "message": f"Unknown action: {action}"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
