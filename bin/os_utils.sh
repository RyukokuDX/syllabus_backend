#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: v2.5.0
# Project Version: v2.5.0
# Last Updated: 2025-07-03

# スクリプトの絶対パスを取得
OS_UTILS_SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" &> /dev/null && pwd )"

# binディレクトリ内のスクリプトファイルの実行権限を復元
restore_execute_permissions() {
    if [ -d "$OS_UTILS_SCRIPT_DIR" ]; then
        find "$OS_UTILS_SCRIPT_DIR" -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || true
    fi
}

# 初回実行時に権限を復元
restore_execute_permissions

# OS種類の判別
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        *)          echo "unknown" ;;
    esac
}

# OS別のコマンド設定を初期化
init_os_commands() {
    local os_type=$(detect_os)
    

    
    if [ "$os_type" = "macos" ]; then
        # macOS用のコマンド
        export LS_VERSION_CMD="ls -1"  # macOSでは -v オプションが利用できないため -1 を使用
        export SORT_CMD="sort -V"      # バージョン番号でソート
        export GREP_CMD="grep"         # macOS用のgrep
        export CUT_CMD="cut"           # macOS用のcut
        export SED_CMD="sed -i ''"     # macOS用のsed（BSD版）

    else
        # Linux用のコマンド
        export LS_VERSION_CMD="ls -v"  # Linuxでは -v オプションが利用可能
        export SORT_CMD="sort -V"      # バージョン番号でソート
        export GREP_CMD="grep"         # Linux用のgrep
        export CUT_CMD="cut"           # Linux用のcut
        export SED_CMD="sed -i"        # Linux用のsed（GNU版）

    fi
    
    echo "$os_type"
}

# 環境変数から値を取得する共通関数
get_env_value() {
    local key="$1"
    local env_file="$2"
    
    if [ -z "$env_file" ]; then
        # デフォルトはプロジェクトルートの.envファイル
        # OS_UTILS_SCRIPT_DIRがbinディレクトリの場合はその親、そうでなければOS_UTILS_SCRIPT_DIR自体
        if [ "$(basename "$OS_UTILS_SCRIPT_DIR")" = "bin" ]; then
            env_file="$(dirname "$OS_UTILS_SCRIPT_DIR")/.env"
        else
            env_file="$OS_UTILS_SCRIPT_DIR/.env"
        fi
    fi
    
    # OS別の処理（将来的な拡張のため）
    local os_type=$(detect_os)
    
    # コマンドが未定義の場合は直接使用
    local grep_cmd="${GREP_CMD:-grep}"
    local cut_cmd="${CUT_CMD:-cut}"
    
    # 基本的にはgrepとcutを使用
    local value=$($grep_cmd "^${key}=" "$env_file" | $cut_cmd -d '=' -f2-)
    
    # 前後の空白を削除
    echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}

# バージョンディレクトリを取得する共通関数
get_version_dirs() {
    local base_dir="$1"
    local pattern="$2"
    
    if [ -z "$base_dir" ]; then
        base_dir="version"
    fi
    
    if [ -z "$pattern" ]; then
        pattern="v*"
    fi
    
    local os_type=$(detect_os)
    
    # コマンドが未定義の場合は直接使用
    local ls_version_cmd="${LS_VERSION_CMD:-ls -v}"
    local sort_cmd="${SORT_CMD:-sort -V}"
    
    if [ "$os_type" = "macos" ]; then
        # macOS: ls -1 で取得して sort -V でソート
        $ls_version_cmd "${base_dir}/${pattern}" 2>/dev/null | $sort_cmd
    else
        # Linux: ls -v で直接ソート済みで取得
        $ls_version_cmd "${base_dir}/${pattern}" 2>/dev/null
    fi
} 