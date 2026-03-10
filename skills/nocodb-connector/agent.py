#!/usr/bin/env python33
import json
import sys

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "缺少参数"}))
        return
    
    try:
        params = json.loads(sys.argv[1])
        action = params.get("action", "test")
        
        if action == "test":
            print(json.dumps({
                "status": "success",
                "message": "Skill运行正常",
                "skill": "nocodb-connector",
                "version": "1.0.0"
            }))
        else:
            print(json.dumps({
                "status": "success",
                "message": f"执行动作: {action}",
                "params": params
            }))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

if __name__ == "__main__":
    main()
