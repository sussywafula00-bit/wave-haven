#!/bin/bash
# Data Tools Wrapper
# 便捷访问 pandas/openpyxl 数据处理工具

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/data-tools-env/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "错误：虚拟环境未找到"
    exit 1
fi

"$VENV_PYTHON" "$@"