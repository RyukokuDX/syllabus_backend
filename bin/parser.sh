#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARSER_DIR="$SCRIPT_DIR/../src/db/parser"
VENV_DIR="$SCRIPT_DIR/../venv_syllabus_backend"
PYTHON="$VENV_DIR/bin/python3"
PROJECT_ROOT="$SCRIPT_DIR/.."

# 仮想環境の確認と作成
if [ ! -d "$VENV_DIR" ]; then
    echo "仮想環境が見つかりません。作成します..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "エラー: 仮想環境の作成に失敗しました。"
        exit 1
    fi
    echo "仮想環境を作成しました。"
fi

# 仮想環境のPythonインタプリタの確認
if [ ! -f "$PYTHON" ]; then
    echo "エラー: 仮想環境のPythonインタプリタが見つかりません。"
    echo "仮想環境を再作成します..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "エラー: 仮想環境の再作成に失敗しました。"
        exit 1
    fi
    echo "仮想環境を再作成しました。"
fi

# 利用可能なパーサーの一覧を動的に生成
declare -A PARSERS
for file in "$PARSER_DIR"/*.py; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        number=${filename%%_*}  # ファイル名の先頭の数字を取得
        name=${filename%%.py}   # .pyを除いたファイル名
        PARSERS["$number"]="$filename"
        PARSERS["$name"]="$filename"
    fi
done

# ヘルプメッセージを表示
show_help() {
    echo "Usage: $0 [PARSER_NAME_OR_NUMBER]"
    echo
    echo "Available parsers:"
    for number in "${!PARSERS[@]}"; do
        if [[ $number =~ ^[0-9]+$ ]]; then  # 数字の場合のみ表示
            name=${PARSERS[$number]%%.py}   # .pyを除いたファイル名
            echo "  $number or $name - ${name#*_} parser"  # 数字と_を除いた名前を表示
        fi
    done | sort -n  # 数字でソート
    echo
    echo "Examples:"
    echo "  $0 01          # Run class parser"
    echo "  $0 class       # Run class parser"
    echo "  $0 02          # Run subclass parser"
    echo "  $0 subclass    # Run subclass parser"
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
cd "$PARSER_DIR" && PYTHONPATH="$PROJECT_ROOT/src" "$PYTHON" "$PARSER_FILE" 