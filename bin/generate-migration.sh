#!/bin/bash
# File Version: v2.4.0
# Project Version: v2.4.0
# Last Updated: 2025-07-03

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
VENV_DIR="$PROJECT_ROOT/venv_syllabus_backend"
PYTHON="$VENV_DIR/bin/python"

# Pythonスクリプトのパス
PYTHON_SCRIPT="$PROJECT_ROOT/src/db/migrations/generate_migration.py"

# 仮想環境が存在するか確認
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found. Please run './syllabus.sh venv-init' first."
    exit 1
fi

# Pythonスクリプトを実行
echo "Generating migration files..."
"$PYTHON" "$PYTHON_SCRIPT"

# 終了コードを確認
if [ $? -eq 0 ]; then
    echo "Migration files generated successfully"
    exit 0
else
    echo "Error: Failed to generate migration files"
    exit 1
fi 