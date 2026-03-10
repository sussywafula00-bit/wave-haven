#!/usr/bin/env python3
"""
Nova Agent 协调器 - 完整测试和集成
测试所有 7 个 Agent 的调用功能
"""

import subprocess
import json
import time
from typing import Dict, List
from datetime import datetime

class NovaAgentCoordinator:
    """Nova Agent 协调器 - 集成版本"""
    
    def __init__(self):
        self.agents = {
            "nova": {"name": "浪潮指挥官", "role": "系统协调", "timeout": 60},
            "dreamnova": {"name": "推演引擎", "role": "复杂决策推演", "timeout": 120},
            "kiki": {"name": "优化专家", "role": "代码优化", "timeout": 90},
            "coco": {"name": "执行者", "role": "任务执行", "timeout": 60},
            "iris": {"name": "临床项目", "role": "临床试验管理", "timeout": 90},
            "luna": {"name": "记忆管理", "role": "记忆存储检索", "timeout": 60},
            "main": {"name": "主Agent", "role": "基础对话", "timeout": 60}
        }
        self.test_results = {}
    
    def call_agent(self, agent_id: str, task: str, context: str = "", timeout: int = None) -> Dict:
        """调用指定 Agent"""
        if agent_id not in self.agents:
            return {"success": False, "error": f"未知 Agent: {agent_id}"}
        
        agent_info = self.agents[agent_id]
        timeout = timeout or agent_info["timeout"]
        
        print(f"\n🌊 调用 {agent_id} ({agent_info['name']})")
        print(f"   角色: {agent_info['role']}")
        print(f"   任务: {task[:50]}...")
        
        # 构建消息
        full_message = task
        if context:
            full_message = f"【上下文信息】\n{context}\n\n【当前任务】\n{task}"
        
        try:
            start_time = time.time()
            result = subprocess.run(
                ['openclaw', 'agent', '--agent', agent_id, '--message', full_message, '--json'],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed = time.time() - start_time
            
            if result.returncode == 0:
                try:
                    data = json.loads(result.stdout)
                    output = data.get('result', {}).get('payloads', [{}])[0].get('text', '')
                    print(f"   ✅ 成功 ({elapsed:.1f}s)")
                    print(f"   输出: {output[:80]}...")
                    return {
                        "success": True,
                        "agent": agent_id,
                        "output": output,
                        "elapsed": elapsed,
                        "error": None
                    }
                except Exception as e:
                    print(f"   ❌ 解析失败: {e}")
                    return {"success": False, "agent": agent_id, "error": f"解析失败: {e}"}
            else:
                print(f"   ❌ 执行失败: {result.stderr[:100]}")
                return {"success": False, "agent": agent_id, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            print(f"   ⏱️ 超时 ({timeout}s)")
            return {"success": False, "agent": agent_id, "error": "执行超时"}
        except Exception as e:
            print(f"   ❌ 异常: {e}")
            return {"success": False, "agent": agent_id, "error": str(e)}
    
    def test_all_agents(self) -> Dict:
        """测试所有 Agent"""
        print("=" * 70)
        print("🧪 Nova Agent 协调器 - 全量测试")
        print("=" * 70)
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试 Agent 数量: {len(self.agents)}")
        print("=" * 70)
        
        # 测试任务（简单，确保快速完成）
        test_tasks = {
            "nova": "简单回复'Nova 就绪'",
            "dreamnova": "简单回复'DreamNova 就绪'",
            "kiki": "简单回复'Kiki 就绪'",
            "coco": "简单回复'Coco 就绪'",
            "iris": "简单回复'Iris 就绪'",
            "luna": "简单回复'Luna 就绪'",
            "main": "简单回复'Main 就绪'"
        }
        
        results = {}
        passed = 0
        failed = 0
        
        for i, (agent_id, task) in enumerate(test_tasks.items(), 1):
            print(f"\n【测试 {i}/{len(test_tasks)}】")
            result = self.call_agent(agent_id, task, timeout=30)
            results[agent_id] = result
            
            if result["success"]:
                passed += 1
            else:
                failed += 1
            
            # 短暂延迟，避免请求过快
            time.sleep(1)
        
        # 汇总
        print("\n" + "=" * 70)
        print("📊 测试结果汇总")
        print("=" * 70)
        
        for agent_id, result in results.items():
            status = "✅ 通过" if result["success"] else "❌ 失败"
            elapsed = f"({result.get('elapsed', 0):.1f}s)" if result.get("elapsed") else ""
            print(f"  {status} {agent_id:12} {elapsed}")
            if not result["success"]:
                print(f"       错误: {result['error'][:60]}")
        
        print("=" * 70)
        print(f"总计: {passed} 通过, {failed} 失败")
        print(f"成功率: {passed/len(results)*100:.1f}%")
        print("=" * 70)
        
        self.test_results = results
        return {
            "success": failed == 0,
            "passed": passed,
            "failed": failed,
            "total": len(results),
            "results": results
        }
    
    def execute_workflow(self, workflow: List[Dict]) -> Dict:
        """执行多 Agent 工作流"""
        print("\n" + "=" * 70)
        print("🌊 执行多 Agent 工作流")
        print("=" * 70)
        
        step_results = {}
        full_context = ""
        
        for i, step in enumerate(workflow, 1):
            agent_id = step["agent"]
            task = step["task"]
            use_context = step.get("use_context", False)
            
            print(f"\n步骤 {i}/{len(workflow)}: {agent_id}")
            print("-" * 70)
            
            # 构建上下文
            context = full_context if use_context else ""
            
            # 调用 Agent
            result = self.call_agent(agent_id, task, context)
            step_results[agent_id] = result
            
            if not result["success"]:
                print(f"\n❌ 工作流中断: {agent_id} 失败")
                return {
                    "success": False,
                    "completed_steps": i - 1,
                    "failed_step": agent_id,
                    "error": result["error"],
                    "results": step_results
                }
            
            # 更新上下文
            if step.get("add_to_context", True):
                full_context += f"\n\n【{self.agents[agent_id]['name']} 的输出】\n{result['output']}"
        
        print("\n" + "=" * 70)
        print("✅ 工作流完成")
        print("=" * 70)
        
        return {
            "success": True,
            "completed_steps": len(workflow),
            "results": step_results,
            "final_context": full_context
        }


# ==================== 测试执行 ====================

if __name__ == "__main__":
    coordinator = NovaAgentCoordinator()
    
    # 第一步: 测试所有 Agent
    print("\n" + "🧪 " * 20)
    test_result = coordinator.test_all_agents()
    
    # 第二步: 如果全部通过，演示工作流
    if test_result["success"]:
        print("\n\n🎉 所有 Agent 测试通过！")
        print("\n准备演示工作流...")
        time.sleep(2)
        
        # 简化的工作流演示
        demo_workflow = [
            {
                "agent": "dreamnova",
                "task": "分析：出海项目的3个关键风险和2个机遇，用 bullet points",
                "use_context": False,
                "add_to_context": True
            },
            {
                "agent": "coco",
                "task": "基于上述分析，生成一份简洁的执行建议（3-5条）",
                "use_context": True,
                "add_to_context": True
            }
        ]
        
        workflow_result = coordinator.execute_workflow(demo_workflow)
        
        if workflow_result["success"]:
            print("\n📋 最终结果:")
            final_agent = demo_workflow[-1]["agent"]
            print(workflow_result["results"][final_agent]["output"])
    else:
        print("\n⚠️  部分 Agent 测试失败，请检查配置")
        print("\n可用的 Agent:")
        for agent_id, result in test_result["results"].items():
            if result["success"]:
                print(f"  ✅ {agent_id}")
