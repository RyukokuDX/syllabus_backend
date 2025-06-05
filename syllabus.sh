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