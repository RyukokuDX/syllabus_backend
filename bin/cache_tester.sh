#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: v2.6.0
# Project Version: v2.6.0
# Last Updated: 2025-07-05

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# OS別コマンド設定の読み込み
source "$SCRIPT_DIR/os_utils.sh"
OS_TYPE=$(init_os_commands)

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
DB_NAME=$(get_env_value "POSTGRES_DB" "$ENV_FILE")
DB_USER=$(get_env_value "POSTGRES_USER" "$ENV_FILE")

# 出力ファイル名
OUTPUT_FILE="$PROJECT_DIR/tests/json_output/intelligent_info_courses.json"

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [オプション]"
    echo
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -o, --output   出力ファイル名を指定（デフォルト: tests/json_output/intelligent_info_courses.json）"
    echo
    echo "説明:"
    echo "  知能情報メディア課程の履修情報のみを絞ったJSONリストファイルを出力します。"
    echo "  出力ファイルには、学部課程が「知能情報メディア課程」の科目のみが含まれます。"
    echo "  フィールド名は新しい命名規則に従い、配列フィールドは「一覧」語尾を使用します。"
    echo
    echo "使用例:"
    echo "  $0                                    # デフォルトファイル名で出力"
    echo "  $0 -o custom_output.json             # カスタムファイル名で出力"
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

# 知能情報課程の履修情報を取得してJSONファイルに出力
generate_intelligent_info_courses() {
    echo -e "${BLUE}知能情報メディア課程の履修情報を取得中...${NC}"
    echo -e "${BLUE}新しい命名規則（一覧語尾）を使用します${NC}"
    
    # 出力ディレクトリの作成
    create_output_directory
    
    # 知能情報課程の履修情報を取得（キャッシュテーブルから）
    # 新しい命名規則: 開講情報一覧、履修情報一覧、シラバス一覧、履修要綱一覧、対象学部課程一覧
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    WITH filtered_cache AS (
        SELECT 
            subject_name_id,
            jsonb_build_object(
                '科目名', cache_data->>'科目名',
                '開講情報一覧', (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            '年度', info->>'年度',
                            'シラバス一覧', (
                                SELECT jsonb_agg(syllabus)
                                FROM jsonb_array_elements(info->'シラバス一覧') AS syllabus
                                WHERE syllabus->'対象学部課程一覧' @> '[\"知能情報メディア課程\"]'
                            )
                        )
                    )
                    FROM jsonb_array_elements(cache_data->'開講情報一覧') AS info
                    WHERE jsonb_typeof(info->'シラバス一覧') = 'array'
                    AND EXISTS (
                        SELECT 1
                        FROM jsonb_array_elements(info->'シラバス一覧') AS syllabus
                        WHERE syllabus->'対象学部課程一覧' @> '[\"知能情報メディア課程\"]'
                    )
                ),
                '履修情報一覧', (
                    SELECT jsonb_agg(
                        jsonb_build_object(
                            '年度', info->>'年度',
                            '履修要綱一覧', (
                                SELECT jsonb_agg(outline)
                                FROM jsonb_array_elements(info->'履修要綱一覧') AS outline
                                WHERE outline->>'学部課程' = '知能情報メディア課程'
                            )
                        )
                    )
                    FROM jsonb_array_elements(cache_data->'履修情報一覧') AS info
                    WHERE jsonb_typeof(info->'履修要綱一覧') = 'array'
                    AND EXISTS (
                        SELECT 1
                        FROM jsonb_array_elements(info->'履修要綱一覧') AS outline
                        WHERE outline->>'学部課程' = '知能情報メディア課程'
                    )
                )
            ) as filtered_data
        FROM syllabus_cache
        WHERE cache_name = 'subject_syllabus_cache'
        AND cache_data->'履修情報一覧' @> '[{\"履修要綱一覧\": [{\"学部課程\": \"知能情報メディア課程\"}]}]'
    )
    SELECT json_agg(filtered_data) as courses
    FROM filtered_cache
    WHERE filtered_data->'履修情報一覧' IS NOT NULL;
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
        echo -e "${RED}知能情報メディア課程の履修情報の出力に失敗しました${NC}"
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
            *)
                echo -e "${RED}エラー: 不明なオプション '$1'${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 知能情報メディア課程の履修情報を生成
    generate_intelligent_info_courses
}

# スクリプトの実行
main "$@" 