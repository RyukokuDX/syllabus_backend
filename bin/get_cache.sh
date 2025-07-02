#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: v2.3.0
# Project Version: v2.3.0
# Last Updated: 2025-07-02

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# .envファイルの読み込み
ENV_FILE="$PROJECT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "エラー: .envファイルが見つかりません: $ENV_FILE"
    exit 1
fi
set -a
. "$ENV_FILE"
set +a

# 色の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# データベース接続情報
DB_NAME=$(grep POSTGRES_DB .env | cut -d '=' -f2)
DB_USER=$(grep POSTGRES_USER .env | cut -d '=' -f2)

# 出力ファイル名
OUTPUT_FILE="$PROJECT_DIR/tests/json_output/full_cache.json"

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [オプション] コマンド"
    echo
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -o, --output   出力ファイル名を指定（デフォルト: tests/json_output/full_cache.json）"
    echo
    echo "コマンド:"
    echo "  full           全キャッシュデータを取得・整形"
    echo
    echo "説明:"
    echo "  科目別シラバスキャッシュの全データを取得してJSONファイルに出力します。"
    echo "  課程別エンティティは「<エンティティ名>: <値>」の形式で表示されます。"
    echo
    echo "使用例:"
    echo "  $0 full                                    # デフォルトファイル名で出力"
    echo "  $0 -o custom_output.json full             # カスタムファイル名で出力"
    echo ""
}

# 出力ディレクトリの作成
create_output_directory() {
    local output_dir="$(dirname "$OUTPUT_FILE")"
    if [ ! -d "$output_dir" ]; then
        echo -e "${BLUE}出力ディレクトリを作成中: $output_dir${NC}"
        mkdir -p "$output_dir"
    fi
}

# 全キャッシュデータを取得してJSONファイルに出力
generate_full_cache() {
    echo -e "${BLUE}全キャッシュデータを取得中...${NC}"
    
    # 出力ディレクトリの作成
    create_output_directory
    
    # 全キャッシュデータを取得
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT json_agg(cache_data) as full_cache
    FROM syllabus_cache
    WHERE cache_name = 'subject_syllabus_cache';
    " > "$OUTPUT_FILE.raw"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}生データの出力が完了しました${NC}"
        echo -e "${BLUE}生データファイル: $OUTPUT_FILE.raw${NC}"
        
        # 生データのサイズを表示
        file_size=$(du -h "$OUTPUT_FILE.raw" | cut -f1)
        echo -e "${BLUE}生データファイルサイズ: $file_size${NC}"
        
        # JSONの整形を試行
        echo -e "${BLUE}JSONの整形を試行中...${NC}"
        if tail -n +3 "$OUTPUT_FILE.raw" | head -n 1 | jq '.' > "$OUTPUT_FILE" 2>/dev/null; then
            echo -e "${GREEN}JSONの整形が完了しました${NC}"
            echo -e "${BLUE}出力ファイル: $OUTPUT_FILE${NC}"
            
            # 出力された件数を確認
            count=$(jq 'length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
            echo -e "${BLUE}出力された科目数: $count${NC}"
            
            # ファイルサイズを表示
            file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
            echo -e "${BLUE}ファイルサイズ: $file_size${NC}"
        else
            echo -e "${YELLOW}JSONの整形に失敗しました。生データを確認してください。${NC}"
            echo -e "${YELLOW}エラーの詳細を確認するには: jq '.' $OUTPUT_FILE.raw${NC}"
        fi
    else
        echo -e "${RED}全キャッシュデータの出力に失敗しました${NC}"
        exit 1
    fi
}

# メイン処理
main() {
    # コマンドライン引数の解析
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -o|--output)
                if [ -n "$2" ]; then
                    OUTPUT_FILE="$2"
                    shift 2
                else
                    echo -e "${RED}エラー: 出力ファイル名が指定されていません${NC}"
                    exit 1
                fi
                ;;
            full)
                generate_full_cache
                exit 0
                ;;
            *)
                echo -e "${RED}エラー: 不明なオプションまたはコマンド '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # コマンドが指定されていない場合はヘルプを表示
    show_help
    exit 1
}

# スクリプトの実行
main "$@" 