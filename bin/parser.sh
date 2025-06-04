#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARSER_DIR="$SCRIPT_DIR/../src/db/parser"
VENV_DIR="$SCRIPT_DIR/../syllabus_backend_venv"
PYTHON="$VENV_DIR/bin/python"

# 利用可能なパーサーの一覧
declare -A PARSERS=(
    ["06"]="06_book.py"
    ["17"]="17_subject.py"
    ["book"]="06_book.py"
    ["syllabus"]="17_subject.py"
)

# ヘルプメッセージを表示
show_help() {
    echo "Usage: $0 [PARSER_NAME_OR_NUMBER]"
    echo
    echo "Available parsers:"
    echo "  06 or book     - Book parser"
    echo "  17 or syllabus - Subject parser"
    echo
    echo "Examples:"
    echo "  $0 06          # Run book parser"
    echo "  $0 book        # Run book parser"
    echo "  $0 17          # Run subject parser"
    echo "  $0 syllabus    # Run subject parser"
}

# 引数が指定されていない場合はヘルプを表示
if [ -z "$1" ]; then
    show_help
    exit 1
fi

# パーサーの選択
PARSER_NAME="${PARSERS[$1]}"

# パーサーが存在しない場合
if [ -z "$PARSER_NAME" ]; then
    echo "Error: Unknown parser '$1'"
    show_help
    exit 1
fi

# パーサーファイルのパス
PARSER_FILE="$PARSER_DIR/$PARSER_NAME"

# パーサーファイルが存在しない場合
if [ ! -f "$PARSER_FILE" ]; then
    echo "Error: Parser file not found: $PARSER_FILE"
    exit 1
fi

# パーサーの実行
echo "Running parser: $PARSER_NAME"
"$PYTHON" "$PARSER_FILE" 