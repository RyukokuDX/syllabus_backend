#!/bin/bash
# File Version: v3.0.0
# Project Version: v3.0.0
# Last Updated: 2025-07-08

# スクリプトの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "実行権限を復元中..."

# binディレクトリ内のスクリプトファイルの実行権限を復元
if [ -d "$SCRIPT_DIR" ]; then
    echo "binディレクトリ内のスクリプトファイルの権限を復元中..."
    find "$SCRIPT_DIR" -name "*.sh" -type f -exec chmod +x {} \;
    echo "✓ binディレクトリの権限復元完了"
fi

# プロジェクトルートのスクリプトファイルの実行権限を復元
if [ -f "$PROJECT_ROOT/syllabus.sh" ]; then
    echo "プロジェクトルートのスクリプトファイルの権限を復元中..."
    chmod +x "$PROJECT_ROOT/syllabus.sh"
    echo "✓ syllabus.shの権限復元完了"
fi

echo "実行権限の復元が完了しました。" 