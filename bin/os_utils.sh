#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: 2.0.0
# Project Version: 2.4.0
# Last Update: 2025-07-03

# OS種類の判別
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        CYGWIN*)    echo "windows" ;;
        MINGW*)     echo "windows" ;;
        MSYS*)      echo "windows" ;;
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
    else
        # Linux用のコマンド
        export LS_VERSION_CMD="ls -v"  # Linuxでは -v オプションが利用可能
        export SORT_CMD="sort -V"      # バージョン番号でソート
        export GREP_CMD="grep"         # Linux用のgrep
        export CUT_CMD="cut"           # Linux用のcut
    fi
    
    echo "$os_type"
}

# 環境変数から値を取得する共通関数
get_env_value() {
    local key="$1"
    local env_file="$2"
    
    if [ -z "$env_file" ]; then
        env_file=".env"
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