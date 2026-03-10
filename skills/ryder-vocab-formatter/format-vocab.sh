#!/bin/bash
# RyderVocabFormatter 快捷命令
# 用法: ./format-vocab.sh [选项] <输入文件>

SKILL_DIR="$HOME/.openclaw/workspace_shared/skills/ryder-vocab-formatter"
PYTHON_SCRIPT="$SKILL_DIR/formatter.py"

if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "❌ 找不到 formatter.py，请检查 skill 安装路径"
    exit 1
fi

python3 "$PYTHON_SCRIPT" "$@"
