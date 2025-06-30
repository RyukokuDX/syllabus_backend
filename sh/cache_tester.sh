#!/bin/bash
# -*- coding: utf-8 -*-
# File Version: v1.0.1
# Project Version: v2.0.3
# Last Updated: 2025-06-30

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
OUTPUT_FILE="$PROJECT_DIR/output/intelligent_info_courses.json"

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [オプション]"
    echo
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -o, --output   出力ファイル名を指定（デフォルト: output/intelligent_info_courses.json）"
    echo
    echo "説明:"
    echo "  知能情報課程の履修情報のみを絞ったJSONリストファイルを出力します。"
    echo "  出力ファイルには、学部課程が「知能情報課程」の科目のみが含まれます。"
    echo
    echo "使用例:"
    echo "  $0                                    # デフォルトファイル名で出力"
    echo "  $0 -o custom_output.json             # カスタムファイル名で出力"
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
    echo -e "${BLUE}知能情報課程の履修情報を取得中...${NC}"
    
    # 出力ディレクトリの作成
    create_output_directory
    
    # 知能情報課程の履修情報を取得
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -A -F "," -c "
    WITH syllabus_data AS (
        SELECT 
            sm.syllabus_id,
            sm.syllabus_code,
            sm.syllabus_year,
            s.subject_name_id,
            sn.name as subject_name,
            s.subtitle,
            s.term,
            s.campus,
            s.credits,
            s.goals,
            s.summary,
            s.attainment,
            s.methods,
            s.outside_study,
            s.textbook_comment,
            s.reference_comment,
            s.grading_comment,
            s.advice
        FROM syllabus_master sm
        JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
        JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
    ),
    instructor_data AS (
        SELECT 
            si.syllabus_id,
            json_agg(
                json_build_object(
                    '教員名', i.name,
                    '役割', COALESCE(si.role, '担当')
                )
            ) as instructors
        FROM syllabus_instructor si
        JOIN instructor i ON si.instructor_id = i.instructor_id
        GROUP BY si.syllabus_id
    ),
    lecture_time_data AS (
        SELECT 
            lt.syllabus_id,
            json_agg(
                json_build_object(
                    '曜日', lt.day_of_week,
                    '時限', lt.period
                )
            ) as lecture_times,
            json_agg(lt.period) as periods
        FROM lecture_time lt
        GROUP BY lt.syllabus_id
    ),
    textbook_data AS (
        SELECT 
            syllabus_id,
            json_agg(book_info) as textbooks
        FROM (
            -- syllabus_bookから教科書を取得
            SELECT 
                sb.syllabus_id,
                json_build_object(
                    '書名', b.title,
                    '著者', b.author,
                    'ISBN', b.isbn,
                    '値段', b.price,
                    '備考', sb.note
                ) as book_info
            FROM syllabus_book sb
            JOIN book b ON sb.book_id = b.book_id
            WHERE sb.role = '教科書'
            
            UNION ALL
            
            -- book_uncategorizedから教科書を取得
            SELECT 
                bu.syllabus_id,
                json_build_object(
                    '書名', bu.title,
                    '著者', bu.author,
                    'ISBN', bu.isbn,
                    '値段', bu.price,
                    '備考', bu.note
                ) as book_info
            FROM book_uncategorized bu
            WHERE bu.role = '教科書'
        ) combined_textbooks
        GROUP BY syllabus_id
    ),
    reference_data AS (
        SELECT 
            syllabus_id,
            json_agg(book_info) as references
        FROM (
            -- syllabus_bookから参考書を取得
            SELECT 
                sb.syllabus_id,
                json_build_object(
                    '書名', b.title,
                    '著者', b.author,
                    'ISBN', b.isbn,
                    '値段', b.price,
                    '備考', sb.note
                ) as book_info
            FROM syllabus_book sb
            JOIN book b ON sb.book_id = b.book_id
            WHERE sb.role = '参考書'
            
            UNION ALL
            
            -- book_uncategorizedから参考書を取得
            SELECT 
                bu.syllabus_id,
                json_build_object(
                    '書名', bu.title,
                    '著者', bu.author,
                    'ISBN', bu.isbn,
                    '値段', bu.price,
                    '備考', bu.note
                ) as book_info
            FROM book_uncategorized bu
            WHERE bu.role = '参考書'
        ) combined_references
        GROUP BY syllabus_id
    ),
    grading_data AS (
        SELECT 
            gc.syllabus_id,
            json_agg(
                json_build_object(
                    '項目', gc.criteria_type,
                    '割合', gc.ratio,
                    '評価方法', gc.criteria_description,
                    '備考', gc.note
                )
            ) as grading_criteria
        FROM grading_criterion gc
        GROUP BY gc.syllabus_id
    ),
    subject_data AS (
        SELECT 
            sub.subject_name_id,
            sub.curriculum_year,
            json_agg(
                json_build_object(
                    '学部課程', f.faculty_name,
                    '科目区分', c.class_name,
                    '科目小区分', COALESCE(sc.subclass_name, ''),
                    '必須度', sub.requirement_type,
                    '課程別エンティティ', sav.value
                )
            ) as subject_info
        FROM subject sub
        JOIN faculty f ON sub.faculty_id = f.faculty_id
        JOIN class c ON sub.class_id = c.class_id
        LEFT JOIN subclass sc ON sub.subclass_id = sc.subclass_id
        LEFT JOIN subject_attribute_value sav ON sub.subject_id = sav.subject_id
        LEFT JOIN subject_attribute sa ON sav.attribute_id = sa.attribute_id
            AND sa.attribute_name = '課程別エンティティ'
        WHERE f.faculty_name = '知能情報課程'
        GROUP BY sub.subject_name_id, sub.curriculum_year
    ),
    cache_data AS (
        SELECT 
            sd.syllabus_id,
            json_build_object(
                '科目名', sd.subject_name,
                '開講情報', json_agg(
                    json_build_object(
                        '年', sd.syllabus_year,
                        'シラバス', json_build_object(
                            '担当', COALESCE(id.instructors, '[]'::json),
                            '学期', sd.term,
                            '曜日', COALESCE(ltd.lecture_times->0->>'曜日', ''),
                            '時限', COALESCE(ltd.periods, '[]'::json),
                            '単位', sd.credits,
                            '教科書', COALESCE(td.textbooks, '[]'::json),
                            '教科書コメント', sd.textbook_comment,
                            '参考書', COALESCE(rd.references, '[]'::json),
                            '参考書コメント', sd.reference_comment,
                            '成績', COALESCE(gd.grading_criteria, '[]'::json),
                            '成績コメント', sd.grading_comment
                        )
                    )
                ),
                '履修情報', json_agg(
                    json_build_object(
                        '年', subd.curriculum_year,
                        '履修要綱', subd.subject_info
                    )
                )
            ) as cache_data
        FROM syllabus_data sd
        LEFT JOIN instructor_data id ON sd.syllabus_id = id.syllabus_id
        LEFT JOIN lecture_time_data ltd ON sd.syllabus_id = ltd.syllabus_id
        LEFT JOIN textbook_data td ON sd.syllabus_id = td.syllabus_id
        LEFT JOIN reference_data rd ON sd.syllabus_id = rd.syllabus_id
        LEFT JOIN grading_data gd ON sd.syllabus_id = gd.syllabus_id
        LEFT JOIN subject_data subd ON sd.subject_name_id = subd.subject_name_id
        WHERE subd.subject_name_id IS NOT NULL
        GROUP BY sd.subject_name_id, sd.subject_name, sd.syllabus_id
    )
    SELECT json_agg(cd.cache_data) as courses
    FROM cache_data cd;
    " > "$OUTPUT_FILE"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}知能情報課程の履修情報の出力が完了しました${NC}"
        echo -e "${BLUE}出力ファイル: $OUTPUT_FILE${NC}"
        
        # 出力された件数を確認
        count=$(jq 'length' "$OUTPUT_FILE" 2>/dev/null || echo "0")
        echo -e "${BLUE}出力された科目数: $count${NC}"
        
        # ファイルサイズを表示
        file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo -e "${BLUE}ファイルサイズ: $file_size${NC}"
    else
        echo -e "${RED}知能情報課程の履修情報の出力に失敗しました${NC}"
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
    
    # 知能情報課程の履修情報を生成
    generate_intelligent_info_courses
}

# スクリプトの実行
main "$@" 