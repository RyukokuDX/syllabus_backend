#!/bin/bash

# -*- coding: utf-8 -*-
# File Version: v2.5.2
# Project Version: v2.5.2
# Last Updated: 2025-07-04

# スクリプトのディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# binの親ディレクトリをプロジェクトルートとみなす
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"


# OS別コマンド設定の読み込み
source "$SCRIPT_DIR/os_utils.sh"
OS_TYPE=$(init_os_commands)

# .envファイルの読み込み
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
DB_HOST=$(get_env_value "POSTGRES_HOST" "$ENV_FILE")
DB_PORT=$(get_env_value "POSTGRES_PORT" "$ENV_FILE")

# キャッシュテーブル名
CACHE_TABLE="syllabus_cache"

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [オプション] コマンド [キャッシュ名]"
    echo
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo
    echo "コマンド:"
    echo "  generate <cache_name>  指定されたキャッシュを生成"
    echo "  delete <cache_name>    指定されたキャッシュを削除"
    echo "  refresh <cache_name>   指定されたキャッシュを削除して再生成"
    echo "  list                   利用可能なキャッシュ一覧を表示"
    echo "  status                 キャッシュの状態を表示"
    echo "  get <cache_name>        指定されたキャッシュを取得"
    echo
    echo "利用可能なキャッシュ:"
    echo "  subject_syllabus_cache  科目別シラバスキャッシュ"
    echo "  catalogue                EAVカタログキャッシュ"
    echo
    echo "使用例:"
    echo "  $0 generate subject_syllabus_cache  # 科目別シラバスキャッシュを生成"
    echo "  $0 delete subject_syllabus_cache    # 科目別シラバスキャッシュを削除"
    echo "  $0 refresh subject_syllabus_cache   # 科目別シラバスキャッシュを削除して再生成"
    echo "  $0 list                             # キャッシュ一覧を表示"
    echo "  $0 status                           # キャッシュの状態を表示"
    echo "  $0 get subject_syllabus_cache        # 科目別シラバスキャッシュを取得"
}

# キャッシュテーブルの作成
create_cache_table() {
    echo -e "${BLUE}キャッシュテーブルを作成中...${NC}"
    
    # 既存のテーブルが古い構造の場合は削除
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    DROP TABLE IF EXISTS $CACHE_TABLE CASCADE;
    "
    
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    CREATE TABLE $CACHE_TABLE (
        cache_id SERIAL PRIMARY KEY,
        cache_name VARCHAR(100) NOT NULL,
        subject_name_id INTEGER NOT NULL,
        cache_data JSONB NOT NULL,
        cache_version VARCHAR(10) NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
        UNIQUE(cache_name, subject_name_id)
    );
    
    -- インデックス
    CREATE INDEX idx_${CACHE_TABLE}_cache_name ON $CACHE_TABLE(cache_name);
    CREATE INDEX idx_${CACHE_TABLE}_subject_name_id ON $CACHE_TABLE(subject_name_id);
    CREATE INDEX idx_${CACHE_TABLE}_data ON $CACHE_TABLE USING GIN (cache_data);
    CREATE INDEX idx_${CACHE_TABLE}_version ON $CACHE_TABLE(cache_version);
    "
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}キャッシュテーブルの作成が完了しました${NC}"
    else
        echo -e "${RED}キャッシュテーブルの作成に失敗しました${NC}"
        exit 1
    fi
}

# 科目別シラバスキャッシュの生成
generate_subject_syllabus_cache() {
    echo -e "${BLUE}科目別シラバスキャッシュを生成中...${NC}"
    # 既存のキャッシュを削除
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    DELETE FROM $CACHE_TABLE WHERE cache_name = 'subject_syllabus_cache';
    "
    # キャッシュデータを生成して挿入
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
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
        LEFT JOIN syllabus s ON sm.syllabus_id = s.syllabus_id
        LEFT JOIN subject_name sn ON s.subject_name_id = sn.subject_name_id
    ),
    instructor_data AS (
        SELECT 
            si.syllabus_id,
            COALESCE(json_agg(
                json_build_object(
                    '氏名', i.name,
                    '役割', COALESCE(si.role, '担当')
                )
            ) FILTER (WHERE i.instructor_id IS NOT NULL), '[]'::json) as instructors
        FROM syllabus_instructor si
        LEFT JOIN instructor i ON si.instructor_id = i.instructor_id
        GROUP BY si.syllabus_id
    ),
    lecture_time_data AS (
        SELECT 
            lt.syllabus_id,
            COALESCE(json_agg(
                json_build_object(
                    '曜日', lt.day_of_week,
                    '時限', lt.period
                )
            ) FILTER (WHERE lt.period IS NOT NULL), '[]'::json) as lecture_times,
            COALESCE(json_agg(lt.period) FILTER (WHERE lt.period IS NOT NULL), '[]'::json) as periods
        FROM lecture_time lt
        GROUP BY lt.syllabus_id
    ),
    textbook_data AS (
        SELECT 
            syllabus_id,
            COALESCE(json_agg(book_info), '[]'::json) as textbooks
        FROM (
            -- syllabus_bookから教科書を取得
            SELECT 
                sb.syllabus_id,
                json_build_object(
                    '書名', b.title,
                    '著者', b.author,
                    'ISBN', b.isbn,
                    '価格', b.price
                ) as book_info
            FROM syllabus_book sb
            LEFT JOIN book b ON sb.book_id = b.book_id
            WHERE sb.role = '教科書'
            
            UNION ALL
            
            -- book_uncategorizedから教科書を取得
            SELECT 
                bu.syllabus_id,
                json_build_object(
                    '書名', bu.title,
                    '著者', bu.author,
                    'ISBN', bu.isbn,
                    '価格', bu.price
                ) as book_info
            FROM book_uncategorized bu
            WHERE bu.role = '教科書'
        ) combined_textbooks
        GROUP BY syllabus_id
    ),
    reference_data AS (
        SELECT 
            syllabus_id,
            COALESCE(json_agg(book_info), '[]'::json) as references
        FROM (
            -- syllabus_bookから参考書を取得
            SELECT 
                sb.syllabus_id,
                json_build_object(
                    '書名', b.title,
                    '著者', b.author,
                    'ISBN', b.isbn,
                    '価格', b.price
                ) as book_info
            FROM syllabus_book sb
            LEFT JOIN book b ON sb.book_id = b.book_id
            WHERE sb.role = '参考書'
            
            UNION ALL
            
            -- book_uncategorizedから参考書を取得
            SELECT 
                bu.syllabus_id,
                json_build_object(
                    '書名', bu.title,
                    '著者', bu.author,
                    'ISBN', bu.isbn,
                    '価格', bu.price
                ) as book_info
            FROM book_uncategorized bu
            WHERE bu.role = '参考書'
        ) combined_references
        GROUP BY syllabus_id
    ),
    faculty_data AS (
        SELECT 
            sf.syllabus_id,
            COALESCE(json_agg(f.faculty_name), '[]'::json) as faculties
        FROM syllabus_faculty sf
        LEFT JOIN faculty f ON sf.faculty_id = f.faculty_id
        GROUP BY sf.syllabus_id
    ),
    grading_data AS (
        SELECT 
            gc.syllabus_id,
            COALESCE(json_agg(
                json_build_object(
                    '項目', gc.criteria_type,
                    '割合', gc.ratio,
                    '評価方法', gc.criteria_description,
                    '備考', gc.note
                )
            ) FILTER (WHERE gc.criteria_type IS NOT NULL), '[]'::json) as grading_criteria
        FROM grading_criterion gc
        GROUP BY gc.syllabus_id
    ),
    subject_data AS (
        SELECT 
            sub.subject_name_id,
            sub.curriculum_year,
            COALESCE(json_agg(
                jsonb_strip_nulls(
                    jsonb_build_object(
                        '学部課程', f.faculty_name,
                        '科目区分', c.class_name,
                        '科目小区分', COALESCE(sc.subclass_name, ''),
                        '必須度', sub.requirement_type
                    ) || 
                    COALESCE(
                        (
                            SELECT jsonb_object_agg(
                                CASE WHEN sa.attribute_name = '学修プログラム' THEN '学修プログラム一覧' ELSE sa.attribute_name END,
                                CASE WHEN sa.attribute_name = '学修プログラム' THEN (
                                    SELECT jsonb_agg(sav2.value)
                                    FROM subject_attribute_value sav2
                                    WHERE sav2.subject_id = sub.subject_id AND sav2.attribute_id = sa.attribute_id
                                ) ELSE to_jsonb(sav.value) END
                            )
                            FROM subject_attribute_value sav
                            JOIN subject_attribute sa ON sav.attribute_id = sa.attribute_id
                            WHERE sav.subject_id = sub.subject_id
                        ), '{}'
                    )
                )
            ) FILTER (WHERE f.faculty_name IS NOT NULL), '[]'::json) as subject_info
        FROM subject sub
        LEFT JOIN faculty f ON sub.faculty_id = f.faculty_id
        LEFT JOIN class c ON sub.class_id = c.class_id
        LEFT JOIN subclass sc ON sub.subclass_id = sc.subclass_id
        GROUP BY sub.subject_name_id, sub.curriculum_year
    ),
    syllabus_by_year AS (
        SELECT 
            sd.subject_name_id,
            sd.subject_name,
            sd.syllabus_year,
            COALESCE(json_agg(
                json_build_object(
                    '担当教員一覧', COALESCE(id.instructors, '[]'::json),
                    '対象学部課程一覧', COALESCE(fd.faculties, '[]'::json),
                    '学期', sd.term,
                    '講義時間一覧', COALESCE(ltd.lecture_times, '[]'::json),
                    '単位数', sd.credits,
                    '教科書一覧', COALESCE(td.textbooks, '[]'::json),
                    '教科書コメント', sd.textbook_comment,
                    '参考書一覧', COALESCE(rd.references, '[]'::json),
                    '参考書コメント', sd.reference_comment,
                    '成績評価基準一覧', COALESCE(gd.grading_criteria, '[]'::json),
                    '成績評価コメント', sd.grading_comment
                )
            ) FILTER (WHERE sd.syllabus_id IS NOT NULL), '[]'::json) as syllabi
        FROM syllabus_data sd
        LEFT JOIN instructor_data id ON sd.syllabus_id = id.syllabus_id
        LEFT JOIN faculty_data fd ON sd.syllabus_id = fd.syllabus_id
        LEFT JOIN lecture_time_data ltd ON sd.syllabus_id = ltd.syllabus_id
        LEFT JOIN textbook_data td ON sd.syllabus_id = td.syllabus_id
        LEFT JOIN reference_data rd ON sd.syllabus_id = rd.syllabus_id
        LEFT JOIN grading_data gd ON sd.syllabus_id = gd.syllabus_id
        GROUP BY sd.subject_name_id, sd.subject_name, sd.syllabus_year
    ),
    cache_data AS (
        SELECT 
            sby.subject_name_id,
            json_build_object(
                '科目名', sby.subject_name,
                '開講情報一覧', COALESCE(json_agg(
                    json_build_object(
                        '年度', sby.syllabus_year,
                        'シラバス一覧', sby.syllabi
                    )
                ) FILTER (WHERE sby.syllabus_year IS NOT NULL), '[]'::json),
                '履修情報一覧', COALESCE(json_agg(
                    json_build_object(
                        '年度', subd.curriculum_year,
                        '履修要綱一覧', COALESCE(subd.subject_info, '[]'::json)
                    )
                ) FILTER (WHERE subd.curriculum_year IS NOT NULL), '[]'::json)
            ) as cache_data
        FROM syllabus_by_year sby
        LEFT JOIN subject_data subd ON sby.subject_name_id = subd.subject_name_id
        GROUP BY sby.subject_name_id, sby.subject_name
    )
    INSERT INTO $CACHE_TABLE (cache_name, subject_name_id, cache_data, cache_version)
    SELECT 
        'subject_syllabus_cache',
        cd.subject_name_id,
        cd.cache_data,
        'v2.4.1'
    FROM cache_data cd;
    "
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}科目別シラバスキャッシュの生成が完了しました${NC}"
        # 生成されたキャッシュの件数を表示
        count=$(docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -c "
        SELECT COUNT(*) FROM $CACHE_TABLE WHERE cache_name = 'subject_syllabus_cache';
        " | tr -d ' ')
        echo -e "${BLUE}生成されたキャッシュ件数: $count${NC}"
    else
        echo -e "${RED}科目別シラバスキャッシュの生成に失敗しました${NC}"
        exit 1
    fi
}

# EAVカタログキャッシュの生成
generate_catalogue_cache() {
    echo -e "${BLUE}EAVカタログキャッシュを生成中...${NC}"
    # 既存のキャッシュを削除
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    DELETE FROM $CACHE_TABLE WHERE cache_name = 'catalogue';
    "
    # EAVカタログ生成SQL（全attribute_name＋科目区分・小区分・対象学部一覧）
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    WITH eav_catalog AS (
      SELECT
        jsonb_object_agg(attribute_name, values) AS catalog
      FROM (
        SELECT
          sa.attribute_name,
          jsonb_agg(DISTINCT sav.value ORDER BY sav.value) AS values
        FROM subject_attribute sa
        LEFT JOIN subject_attribute_value sav ON sa.attribute_id = sav.attribute_id
        WHERE sav.value IS NOT NULL AND sav.value <> ''
        GROUP BY sa.attribute_name
      ) t
    ),
    class_catalog AS (
      SELECT jsonb_agg(class_name ORDER BY class_name) AS class_list FROM class
    ),
    subclass_catalog AS (
      SELECT jsonb_agg(subclass_name ORDER BY subclass_name) AS subclass_list FROM subclass
    ),
    faculty_catalog AS (
      SELECT jsonb_agg(faculty_name ORDER BY faculty_name) AS faculty_list FROM faculty
    ),
    merged_catalog AS (
      SELECT 
        eav_catalog.catalog
        || jsonb_build_object('科目区分', class_catalog.class_list)
        || jsonb_build_object('科目小区分', subclass_catalog.subclass_list)
        || jsonb_build_object('対象学部一覧', faculty_catalog.faculty_list)
      AS full_catalog
      FROM eav_catalog, class_catalog, subclass_catalog, faculty_catalog
    )
    INSERT INTO $CACHE_TABLE (cache_name, subject_name_id, cache_data, cache_version)
    SELECT
      'catalogue',
      0,
      full_catalog,
      'v1.0.0'
    FROM merged_catalog;
    "
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}EAVカタログキャッシュの生成が完了しました${NC}"
        count=$(docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -c "SELECT COUNT(*) FROM $CACHE_TABLE WHERE cache_name = 'catalogue';" | tr -d ' ')
        echo -e "${BLUE}生成されたカタログキャッシュ件数: $count${NC}"
    else
        echo -e "${RED}EAVカタログキャッシュの生成に失敗しました${NC}"
        exit 1
    fi
}

# キャッシュの削除
delete_cache() {
    local cache_name="$1"
    
    echo -e "${BLUE}キャッシュ '$cache_name' を削除中...${NC}"
    
    # 削除前の件数を取得
    count=$(docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -c "
    SELECT COUNT(*) FROM $CACHE_TABLE WHERE cache_name = '$cache_name';
    " | tr -d ' ')
    
    # キャッシュを削除
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    DELETE FROM $CACHE_TABLE WHERE cache_name = '$cache_name';
    "
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}キャッシュ '$cache_name' の削除が完了しました${NC}"
        echo -e "${BLUE}削除されたキャッシュ件数: $count${NC}"
    else
        echo -e "${RED}キャッシュ '$cache_name' の削除に失敗しました${NC}"
        exit 1
    fi
}

# キャッシュの削除して再生成
refresh_cache() {
    local cache_name="$1"
    echo -e "${BLUE}キャッシュ '$cache_name' を削除して再生成中...${NC}"
    delete_cache "$cache_name"
    case "$cache_name" in
        subject_syllabus_cache)
            generate_subject_syllabus_cache
            ;;
        catalogue)
            generate_catalogue_cache
            ;;
        *)
            echo -e "${RED}エラー: 不明なキャッシュ名 '$cache_name'${NC}"
            list_caches
            exit 1
            ;;
    esac
    echo -e "${GREEN}キャッシュ '$cache_name' の削除して再生成が完了しました${NC}"
}

# キャッシュ一覧の表示
list_caches() {
    echo -e "${BLUE}利用可能なキャッシュ一覧:${NC}"
    echo "=================================================="
    echo "1. subject_syllabus_cache - 科目別シラバスキャッシュ"
    echo "   - 科目のシラバス情報をJSONB形式でキャッシュ"
    echo "   - 教員、教科書、成績評価、履修情報を含む"
    echo ""
    echo "2. catalogue - EAVカタログキャッシュ"
    echo "   - 各属性（科目区分、科目小区分、学部課程、課程別エンティティ等）の値一覧をJSONBでキャッシュ"
    echo "   - LLMやUIの候補値提示、クエリ自動生成に利用"
    echo ""
}

# キャッシュの状態表示
show_cache_status() {
    echo -e "${BLUE}キャッシュの状態:${NC}"
    echo "=================================================="
    
    # 各キャッシュの件数と最終更新日時を表示
    docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
    SELECT 
        cache_name,
        COUNT(*) as record_count,
        MAX(updated_at) as last_updated,
        cache_version
    FROM $CACHE_TABLE
    GROUP BY cache_name, cache_version
    ORDER BY cache_name;
    "
}

# キャッシュの取得
get_cache() {
    local cache_name="$1"
    case "$cache_name" in
        subject_syllabus_cache)
            echo -e "${BLUE}科目別シラバスキャッシュ全件を取得中...${NC}"
            docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT cache_data FROM $CACHE_TABLE WHERE cache_name = 'subject_syllabus_cache';" | "$SCRIPT_DIR/json_prettify.sh"
            ;;
        catalogue)
            echo -e "${BLUE}EAVカタログキャッシュを取得中...${NC}"
            docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -t -A -c "SELECT cache_data FROM $CACHE_TABLE WHERE cache_name = 'catalogue' LIMIT 1;" | "$SCRIPT_DIR/json_prettify.sh"
            ;;
        *)
            echo -e "${RED}エラー: 不明なキャッシュ名 '$cache_name'${NC}"
            list_caches
            exit 1
            ;;
    esac
}

# メイン処理
main() {
    # コマンドライン引数の解析
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    case "$1" in
        -h|--help)
            show_help
            ;;
        generate)
            if [ $# -lt 2 ]; then
                echo -e "${RED}エラー: キャッシュ名が指定されていません${NC}"
                show_help
                exit 1
            fi
            
            # キャッシュテーブルの作成
            create_cache_table
            
            case "$2" in
                subject_syllabus_cache)
                    generate_subject_syllabus_cache
                    ;;
                catalogue)
                    generate_catalogue_cache
                    ;;
                *)
                    echo -e "${RED}エラー: 不明なキャッシュ名 '$2'${NC}"
                    list_caches
                    exit 1
                    ;;
            esac
            ;;
        delete)
            if [ $# -lt 2 ]; then
                echo -e "${RED}エラー: キャッシュ名が指定されていません${NC}"
                show_help
                exit 1
            fi
            
            case "$2" in
                subject_syllabus_cache)
                    delete_cache "$2"
                    ;;
                catalogue)
                    delete_cache "$2"
                    ;;
                *)
                    echo -e "${RED}エラー: 不明なキャッシュ名 '$2'${NC}"
                    list_caches
                    exit 1
                    ;;
            esac
            ;;
        refresh)
            if [ $# -lt 2 ]; then
                echo -e "${RED}エラー: キャッシュ名が指定されていません${NC}"
                show_help
                exit 1
            fi
            
            # キャッシュテーブルの作成
            create_cache_table
            
            case "$2" in
                subject_syllabus_cache)
                    refresh_cache "$2"
                    ;;
                catalogue)
                    refresh_cache "$2"
                    ;;
                *)
                    echo -e "${RED}エラー: 不明なキャッシュ名 '$2'${NC}"
                    list_caches
                    exit 1
                    ;;
            esac
            ;;
        list)
            list_caches
            ;;
        status)
            show_cache_status
            ;;
        get)
            if [ $# -lt 2 ]; then
                echo -e "${RED}エラー: 取得タイプが指定されていません${NC}"
                show_help
                exit 1
            fi
            case "$2" in
                subject_syllabus_cache)
                    get_cache "$2"
                    ;;
                catalogue)
                    get_cache "$2"
                    ;;
                *)
                    echo -e "${RED}エラー: 不明な取得タイプ '$2'${NC}"
                    list_caches
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo -e "${RED}エラー: 不明なコマンド '$1'${NC}"
            show_help
            exit 1
            ;;
    esac
}

# スクリプトの実行
main "$@" 