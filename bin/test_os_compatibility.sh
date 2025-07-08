#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: 1.0.0
# Project Version: 2.0.1
# Last Update: 2025-07-01

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# OS別コマンド設定の読み込み
source "$SCRIPT_DIR/os_utils.sh"

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== OS互換性テスト ===${NC}"
echo

# OS種類の判別テスト
echo -e "${YELLOW}1. OS種類の判別${NC}"
OS_TYPE=$(detect_os)
echo -e "検出されたOS: ${GREEN}$OS_TYPE${NC}"
echo

# OS別コマンド設定のテスト
echo -e "${YELLOW}2. OS別コマンド設定${NC}"
init_os_commands
echo -e "LS_VERSION_CMD: ${GREEN}$LS_VERSION_CMD${NC}"
echo -e "SORT_CMD: ${GREEN}$SORT_CMD${NC}"
echo -e "GREP_CMD: ${GREEN}$GREP_CMD${NC}"
echo -e "CUT_CMD: ${GREEN}$CUT_CMD${NC}"
echo

# バージョンディレクトリ取得のテスト
echo -e "${YELLOW}3. バージョンディレクトリ取得テスト${NC}"
if [ -d "$SCRIPT_DIR/../version" ]; then
    echo "バージョンディレクトリが存在します"
    VERSION_DIRS=($(get_version_dirs "$SCRIPT_DIR/../version" "v*"))
    if [ ${#VERSION_DIRS[@]} -gt 0 ]; then
        echo -e "取得されたバージョンディレクトリ:"
        for dir in "${VERSION_DIRS[@]}"; do
            echo -e "  ${GREEN}$(basename "$dir")${NC}"
        done
    else
        echo -e "${YELLOW}バージョンディレクトリが見つかりません${NC}"
    fi
else
    echo -e "${YELLOW}バージョンディレクトリが存在しません${NC}"
fi
echo

# 環境変数取得のテスト
echo -e "${YELLOW}4. 環境変数取得テスト${NC}"
if [ -f "$SCRIPT_DIR/../.env" ]; then
    echo ".envファイルが存在します"
    # テスト用の環境変数を取得してみる
    DB_NAME=$(get_env_value "POSTGRES_DB" "$SCRIPT_DIR/../.env")
    if [ -n "$DB_NAME" ]; then
        echo -e "POSTGRES_DB: ${GREEN}$DB_NAME${NC}"
    else
        echo -e "${YELLOW}POSTGRES_DBが見つかりません${NC}"
    fi
else
    echo -e "${YELLOW}.envファイルが存在しません${NC}"
fi
echo

# コマンドの互換性テスト
echo -e "${YELLOW}5. コマンドの互換性テスト${NC}"

# lsコマンドのテスト
echo -e "ls -v コマンドのテスト:"
if ls -v /dev/null >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓ ls -v が利用可能です${NC}"
else
    echo -e "  ${YELLOW}✗ ls -v が利用できません${NC}"
fi

# sort -V コマンドのテスト
echo -e "sort -V コマンドのテスト:"
if echo "v1.0 v2.0 v1.1" | tr ' ' '\n' | sort -V >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓ sort -V が利用可能です${NC}"
else
    echo -e "  ${YELLOW}✗ sort -V が利用できません${NC}"
fi

# grep コマンドのテスト
echo -e "grep コマンドのテスト:"
if echo "test" | grep "test" >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓ grep が利用可能です${NC}"
else
    echo -e "  ${RED}✗ grep が利用できません${NC}"
fi

# cut コマンドのテスト
echo -e "cut コマンドのテスト:"
if echo "key=value" | cut -d '=' -f2 >/dev/null 2>&1; then
    echo -e "  ${GREEN}✓ cut が利用可能です${NC}"
else
    echo -e "  ${RED}✗ cut が利用できません${NC}"
fi
echo

echo -e "${BLUE}=== テスト完了 ===${NC}" 