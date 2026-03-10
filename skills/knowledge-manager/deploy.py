#!/usr/bin/env python3
"""
Knowledge Manager - Agent部署配置工具
用于为特定Agent启用/禁用知识管理功能
"""

import json
import sys
from pathlib import Path
from datetime import datetime

class AgentKnowledgeDeployer:
    """Agent知识系统部署工具"""
    
    def __init__(self):
        self.base_path = Path.home() / ".openclaw"
        self.agents_path = self.base_path / "agents"
    
    def deploy_for_agent(self, agent_name: str, categories: list = None) -> dict:
        """
        为指定Agent部署知识管理系统
        
        Args:
            agent_name: Agent名称 (iris, dreamnova, kiki, luna, nova)
            categories: 该Agent管理的知识类别
        
        Returns:
            部署结果
        """
        agent_path = self.agents_path / agent_name
        
        # 检查Agent是否存在
        if not agent_path.exists():
            return {
                "status": "error",
                "message": f"Agent {agent_name} 不存在"
            }
        
        try:
            # 1. 创建workspace目录（如果不存在）
            workspace_path = agent_path / "workspace"
            workspace_path.mkdir(exist_ok=True)
            
            # 2. 创建knowledge_index.md
            index_path = workspace_path / "knowledge_index.md"
            if not index_path.exists():
                index_content = f"""# {agent_name.upper()} 知识库索引

> 由Knowledge Manager自动生成
> 创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 知识类别

"""
                if categories:
                    for cat in categories:
                        index_content += f"- {cat}\n"
                else:
                    index_content += "- 通用知识\n"
                
                index_content += "\n## 已学习文档\n\n"
                index_path.write_text(index_content, encoding='utf-8')
            
            # 3. 创建mid/temporal目录（如果不存在）
            mid_path = agent_path / "mid" / "temporal"
            mid_path.mkdir(parents=True, exist_ok=True)
            
            # 4. 创建配置标记
            config_path = workspace_path / "knowledge_config.json"
            config = {
                "agent": agent_name,
                "enabled": True,
                "categories": categories or ["general"],
                "deployed_at": datetime.now().isoformat(),
                "auto_index": True,
                "auto_notify": True
            }
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
            
            return {
                "status": "success",
                "agent": agent_name,
                "message": f"已为 {agent_name} 部署知识管理系统",
                "paths": {
                    "index": str(index_path),
                    "config": str(config_path),
                    "memories": str(mid_path)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "agent": agent_name,
                "message": str(e)
            }
    
    def disable_for_agent(self, agent_name: str) -> dict:
        """禁用指定Agent的知识管理（保留数据）"""
        config_path = self.agents_path / agent_name / "workspace" / "knowledge_config.json"
        
        if not config_path.exists():
            return {
                "status": "warning",
                "message": f"{agent_name} 未启用知识管理"
            }
        
        try:
            config = json.loads(config_path.read_text())
            config["enabled"] = False
            config["disabled_at"] = datetime.now().isoformat()
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2))
            
            return {
                "status": "success",
                "agent": agent_name,
                "message": f"已禁用 {agent_name} 的知识管理（数据保留）"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_deployment_status(self, agent_name: str = None) -> dict:
        """获取部署状态"""
        all_agents = ["iris", "dreamnova", "kiki", "luna", "nova"]
        
        if agent_name:
            all_agents = [agent_name]
        
        results = {}
        for agent in all_agents:
            config_path = self.agents_path / agent / "workspace" / "knowledge_config.json"
            index_path = self.agents_path / agent / "workspace" / "knowledge_index.md"
            mid_path = self.agents_path / agent / "mid" / "temporal"
            
            has_config = config_path.exists()
            has_index = index_path.exists()
            memory_count = len(list(mid_path.glob("*.json"))) if mid_path.exists() else 0
            
            if has_config:
                try:
                    config = json.loads(config_path.read_text())
                    enabled = config.get("enabled", False)
                    categories = config.get("categories", [])
                except:
                    enabled = False
                    categories = []
            else:
                enabled = False
                categories = []
            
            results[agent] = {
                "enabled": enabled,
                "has_config": has_config,
                "has_index": has_index,
                "memory_count": memory_count,
                "categories": categories,
                "status": "active" if enabled and has_index else "inactive"
            }
        
        return results
    
    def recommend_deployment(self) -> dict:
        """推荐部署策略"""
        recommendations = {
            "iris": {
                "priority": "high",
                "reason": "临床运营专家，需要管理出海、GCP、法规等专业知识",
                "categories": ["clinical", "regulatory", "出海"],
                "recommended": True
            },
            "dreamnova": {
                "priority": "medium",
                "reason": "推演分析专家，可存储推演框架、分析方法、决策模型",
                "categories": ["analysis", "framework", "methodology"],
                "recommended": True
            },
            "kiki": {
                "priority": "medium", 
                "reason": "技术优化专家，可存储代码规范、架构模式、最佳实践",
                "categories": ["technical", "coding", "architecture"],
                "recommended": True
            },
            "luna": {
                "priority": "low",
                "reason": "记忆管理专家，本身管理记忆系统，可辅助但不必须",
                "categories": ["memory", "organization"],
                "recommended": False
            },
            "nova": {
                "priority": "low",
                "reason": "系统协调者，主要职责是路由协调，知识需求较少",
                "categories": ["system", "coordination"],
                "recommended": False
            }
        }
        
        return recommendations


def main():
    """主入口"""
    deployer = AgentKnowledgeDeployer()
    
    if len(sys.argv) < 2:
        print("Knowledge Manager - Agent部署工具")
        print("")
        print("用法:")
        print("  python deploy.py status [agent]     - 查看部署状态")
        print("  python deploy.py deploy <agent>     - 为Agent部署知识系统")
        print("  python deploy.py disable <agent>    - 禁用Agent知识系统")
        print("  python deploy.py recommend          - 查看部署建议")
        print("")
        print("示例:")
        print("  python deploy.py status             - 查看所有Agent状态")
        print("  python deploy.py deploy iris        - 为iris部署")
        print("  python deploy.py deploy dreamnova   - 为dreamnova部署")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "status":
        agent = sys.argv[2] if len(sys.argv) > 2 else None
        status = deployer.get_deployment_status(agent)
        
        print("\n" + "="*60)
        print("📊 Knowledge Manager 部署状态")
        print("="*60)
        
        for agent_name, info in status.items():
            status_icon = "🟢" if info["status"] == "active" else "⚪"
            print(f"\n{status_icon} {agent_name.upper()}")
            print(f"   状态: {info['status']}")
            print(f"   已启用: {info['enabled']}")
            print(f"   有索引: {info['has_index']}")
            print(f"   记忆数: {info['memory_count']}")
            if info['categories']:
                print(f"   类别: {', '.join(info['categories'])}")
    
    elif command == "deploy":
        if len(sys.argv) < 3:
            print("错误: 请指定Agent名称")
            sys.exit(1)
        
        agent = sys.argv[2]
        categories = sys.argv[3].split(",") if len(sys.argv) > 3 else None
        
        result = deployer.deploy_for_agent(agent, categories)
        
        print("\n" + "="*60)
        if result["status"] == "success":
            print(f"✅ {result['message']}")
            print("\n创建的文件:")
            for path_type, path in result["paths"].items():
                print(f"  • {path_type}: {path}")
        else:
            print(f"❌ {result['message']}")
        print("="*60)
    
    elif command == "disable":
        if len(sys.argv) < 3:
            print("错误: 请指定Agent名称")
            sys.exit(1)
        
        agent = sys.argv[2]
        result = deployer.disable_for_agent(agent)
        
        print(f"\n{result['message']}")
    
    elif command == "recommend":
        recommendations = deployer.recommend_deployment()
        
        print("\n" + "="*60)
        print("💡 Knowledge Manager 部署建议")
        print("="*60)
        
        for agent, rec in recommendations.items():
            icon = "⭐" if rec["recommended"] else "○"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(rec["priority"], "⚪")
            
            print(f"\n{icon} {agent.upper()} {priority_emoji} {rec['priority']}")
            print(f"   建议: {'推荐部署' if rec['recommended'] else '可选部署'}")
            print(f"   原因: {rec['reason']}")
            print(f"   类别: {', '.join(rec['categories'])}")
    
    else:
        print(f"未知命令: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
