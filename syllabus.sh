#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv_syllabus_backend"
PYTHON="$VENV_DIR/bin/python"

# .envファイルの読み込み
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "エラー: .envファイルが見つかりません: $ENV_FILE"
    exit 1
fi
set -a
. "$ENV_FILE"
set +a

# CSVファイルの整形
normalize_csv() {
    local year="$1"
    local csv_dir="$SCRIPT_DIR/src/course_guide/$year/csv"
    
    if [ ! -d "$csv_dir" ]; then
        echo "エラー: 指定された年度のCSVディレクトリが存在しません: $csv_dir"
        exit 1
    fi
    
    echo "$year年度のCSVファイルを整形中..."
    cd "$SCRIPT_DIR"  # スクリプトのディレクトリに移動
    
    # すべてのCSVファイルを処理
    for csv_file in "$csv_dir"/*.csv; do
        if [ -f "$csv_file" ]; then
            echo "処理中: $(basename "$csv_file")"
            
            # バックアップファイルが存在しない場合のみバックアップを作成
            if [ ! -f "${csv_file}.org" ]; then
                cp "$csv_file" "${csv_file}.org"
                echo "バックアップ作成: $(basename "${csv_file}.org")"
            else
                echo "バックアップは既に存在します: $(basename "${csv_file}.org")"
            fi
            
            PYTHONPATH="$SCRIPT_DIR/src" "$PYTHON" -c "
import sys
import csv
import os
from db.parser.utils import normalize_subject_name

def normalize_csv(input_file):
    # 入力ファイルの区切り文字を判定
    with open(input_file, 'r', encoding='utf-8') as f:
        sample = f.read(4096)
        dialect = csv.Sniffer().sniff(sample)
        delimiter = dialect.delimiter
    
    # 入力ファイルを読み込み
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=delimiter)
        # ヘッダー行を読み取り
        headers = next(reader)
        # 科目名フィールドのインデックスを特定
        subject_name_index = None
        for i, header in enumerate(headers):
            if header.strip() == '科目名':
                subject_name_index = i
                break
        
        if subject_name_index is None:
            print(f'警告: 科目名フィールドが見つかりません: {os.path.basename(input_file)}')
            return
        
        # 残りの行を読み込み
        rows = list(reader)
    
    # 各フィールドを整形
    normalized_rows = []
    for row in rows:
        # 各フィールドの前後の空白を削除し、空文字列をNULLに変換
        normalized_row = []
        for field in row:
            field = field.strip()
            # 空文字列、null、NULL、NoneなどをNULLに統一
            if not field or field.lower() in ['null', 'none', '']:
                normalized_row.append('NULL')
            else:
                normalized_row.append(field)
        
        # 科目名フィールドを正規化
        if len(normalized_row) > subject_name_index and normalized_row[subject_name_index] != 'NULL':
            normalized_row[subject_name_index] = normalize_subject_name(normalized_row[subject_name_index])
        
        normalized_rows.append(normalized_row)
    
    # ヘッダー行と正規化した行を結合
    normalized_rows.insert(0, headers)
    
    # 元のファイルに上書き（タブ区切り）
    with open(input_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(normalized_rows)
    
    print(f'整形完了: {os.path.basename(input_file)}')

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('使用方法: python script.py <input_csv_file>')
        sys.exit(1)
    normalize_csv(sys.argv[1])
" "$csv_file"
        fi
    done
    
    echo "すべてのCSVファイルの整形が完了しました"
}

# 仮想環境の初期化
init_venv() {
    echo "仮想環境を初期化中..."
    if [ -d "$VENV_DIR" ]; then
        echo "仮想環境は既に存在します: $VENV_DIR"
        echo "再作成しますか？ [y/N]"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "既存の仮想環境を削除中..."
            rm -rf "$VENV_DIR"
        else
            echo "既存の仮想環境を維持します"
            return
        fi
    fi
    
    echo "仮想環境を作成中..."
    python3 -m venv "$VENV_DIR"
    
    echo "必要なパッケージをインストール中..."
    cd "$SCRIPT_DIR"  # スクリプトのディレクトリに移動
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install -r requirements.txt
    
    echo "仮想環境の初期化が完了しました"
}

# ヘルプメッセージを表示
show_help() {
    echo "使用方法: $0 [オプション] コマンド [引数]"
    echo
    echo "オプション:"
    echo "  -h, --help     このヘルプメッセージを表示"
    echo "  -p, --postgresql PostgreSQLサービスでコマンドを実行"
    echo
    echo "コマンド:"
    echo "  help           このヘルプメッセージを表示"
    echo "  venv-init      Python仮想環境を初期化"
    echo "  start          指定されたサービスを開始"
    echo "  stop           指定されたサービスを停止"
    echo "  ps             サービスの状態を表示"
    echo "  logs           サービスのログを表示"
    echo "  shell          PostgreSQLサービスのシェルを開く"
    echo "  records        全テーブルのレコード数を表示"
    echo "  parser         指定されたテーブルのパーサースクリプトを実行"
    echo "  generate       指定されたテーブルのデータを生成"
    echo "  check          指定されたテーブルのデータをチェック"
    echo "  deploy         指定されたテーブルのデータをデプロイ"
    echo "  csv normalize 指定年度のCSVファイルを整形（区切り文字をタブに、空白を削除、科目名を正規化）"
    echo
    echo "使用例:"
    echo "  $0 venv-init             # Python仮想環境を初期化"
    echo "  $0 -p start              # PostgreSQLサービスを開始"
    echo "  $0 -p stop               # PostgreSQLサービスを停止"
    echo "  $0 -p shell              # PostgreSQLサービスのシェルを開く"
    echo "  $0 -p records            # レコード数を表示"
    echo "  $0 parser book           # 書籍パーサーを実行"
    echo "  $0 parser syllabus       # シラバスパーサーを実行"
    echo "  $0 parser instructor     # 教員パーサーを実行"
    echo "  $0 -p generate           # 指定されたテーブルのデータを生成"
    echo "  $0 -p check              # 指定されたテーブルのデータをチェック"
    echo "  $0 -p deploy             # 指定されたテーブルのデータをデプロイ"
    echo "  $0 csv normalize 2024    # 2024年度のCSVファイルを整形"
}

# コマンドライン引数の解析
SERVICE=""
COMMAND=""
ARGS=()

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--postgresql)
            SERVICE="postgres"
            shift
            ;;
        *)
            if [ -z "$COMMAND" ]; then
                COMMAND="$1"
            else
                ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

# コマンドが指定されていない場合はヘルプを表示
if [ -z "$COMMAND" ]; then
    show_help
    exit 1
fi

# コマンドの実行
case $COMMAND in
    help)
        show_help
        ;;
    venv-init)
        init_venv
        ;;
    csv)
        if [ ${#ARGS[@]} -eq 0 ]; then
            echo "エラー: CSVコマンドのサブコマンドが指定されていません"
            show_help
            exit 1
        fi
        case "${ARGS[0]}" in
            normalize)
                if [ ${#ARGS[@]} -lt 2 ]; then
                    echo "エラー: 年度が指定されていません"
                    echo "使用方法: $0 csv normalize <year>"
                    exit 1
                fi
                normalize_csv "${ARGS[1]}"
                ;;
            *)
                echo "エラー: 不明なCSVコマンド '${ARGS[0]}'"
                show_help
                exit 1
                ;;
        esac
        ;;
    start)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/start-postgres.sh"
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    stop)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/stop-postgres.sh"
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    ps)
        docker ps
        ;;
    logs)
        if [ "$SERVICE" = "postgres" ]; then
            docker logs -f postgres-db
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    shell)
        if [ "$SERVICE" = "postgres" ]; then
            # .envファイルからデータベース名とユーザー名を取得
            DB_NAME=$(grep POSTGRES_DB .env | cut -d '=' -f2)
            DB_USER=$(grep POSTGRES_USER .env | cut -d '=' -f2)
            docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME"
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    records)
        if [ "$SERVICE" = "postgres" ]; then
            if [ ${#ARGS[@]} -eq 0 ]; then
                # 引数なし: 従来通り全テーブルの件数表示
                DB_NAME=$(grep POSTGRES_DB .env | cut -d '=' -f2)
                DB_USER=$(grep POSTGRES_USER .env | cut -d '=' -f2)
                docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "
                    SELECT 
                        schemaname || '.' || relname as table_name,
                        n_live_tup as record_count
                    FROM pg_stat_user_tables
                    ORDER BY relname;
                "
            else
                # 引数あり: 指定テーブルの全件表示
                TABLE_NAME="${ARGS[0]}"
                DB_NAME=$(grep POSTGRES_DB .env | cut -d '=' -f2)
                DB_USER=$(grep POSTGRES_USER .env | cut -d '=' -f2)
                docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT * FROM $TABLE_NAME;"
            fi
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    parser)
        if [ ${#ARGS[@]} -eq 0 ]; then
            echo "エラー: パーサー名または番号が指定されていません"
            show_help
            exit 1
        fi
        "$SCRIPT_DIR/bin/parser.sh" "${ARGS[@]}"
        ;;
    generate)
        if [ "$SERVICE" = "postgres" ]; then
            if [ ${#ARGS[@]} -eq 0 ]; then
                echo "エラー: 生成タイプが指定されていません"
                echo "使用方法: $0 -p generate [init|migration]"
                exit 1
            fi
            case "${ARGS[0]}" in
                init)
                    echo "初期化データを生成中..."
                    "$SCRIPT_DIR/bin/generate-init.sh"
                    ;;
                migration)
                    echo "マイグレーションデータを生成中..."
                    "$SCRIPT_DIR/bin/generate-migration.sh"
                    ;;
                *)
                    echo "エラー: 不明な生成タイプ '${ARGS[0]}'"
                    echo "使用方法: $0 -p generate [init|migration]"
                    exit 1
                    ;;
            esac
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    check)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/check-with-dev-db.sh"
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    deploy)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/deploy-migration.sh"
        else
            echo "エラー: サービスが指定されていません。PostgreSQLサービスには -p を使用してください。"
            exit 1
        fi
        ;;
    *)
        echo "エラー: 不明なコマンド '$COMMAND'"
        show_help
        exit 1
        ;;
esac 