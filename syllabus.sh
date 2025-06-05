#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv_syllabus_backend"
PYTHON="$VENV_DIR/bin/python"

# .envファイルの読み込み
ENV_FILE="$SCRIPT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: Missing .env file at $ENV_FILE"
    exit 1
fi
set -a
. "$ENV_FILE"
set +a

# 仮想環境の初期化
init_venv() {
    echo "Initializing virtual environment..."
    if [ -d "$VENV_DIR" ]; then
        echo "Virtual environment already exists at $VENV_DIR"
        echo "Do you want to recreate it? [y/N]"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "Removing existing virtual environment..."
            rm -rf "$VENV_DIR"
        else
            echo "Keeping existing virtual environment"
            return
        fi
    fi
    
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    
    echo "Installing required packages..."
    cd "$SCRIPT_DIR"  # スクリプトのディレクトリに移動
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install -r requirements.txt
    
    echo "Virtual environment initialized successfully"
}

# ヘルプメッセージを表示
show_help() {
    echo "Usage: $0 [OPTIONS] COMMAND [ARGS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -p, --postgresql Run command in PostgreSQL service"
    echo
    echo "Commands:"
    echo "  help           Show this help message"
    echo "  venv-init      Initialize Python virtual environment"
    echo "  start          Start the specified service"
    echo "  stop           Stop the specified service"
    echo "  ps             Show service status"
    echo "  logs           Show service logs"
    echo "  shell          Open shell in PostgreSQL service"
    echo "  records        Show record counts for all tables"
    echo "  parser         Run parser script for specified table"
    echo "  generate       Generate data for specified table"
    echo "  check          Check data for specified table"
    echo "  deploy         Deploy data to specified table"
    echo
    echo "Examples:"
    echo "  $0 venv-init             # Initialize Python virtual environment"
    echo "  $0 -p start              # Start PostgreSQL service"
    echo "  $0 -p stop               # Stop PostgreSQL service"
    echo "  $0 -p shell              # Open shell in PostgreSQL service"
    echo "  $0 -p records            # Show record counts"
    echo "  $0 parser book           # Run book parser"
    echo "  $0 parser syllabus       # Run syllabus parser"
    echo "  $0 -p generate           # Generate data for specified table"
    echo "  $0 -p check              # Check data for specified table"
    echo "  $0 -p deploy             # Deploy data to specified table"
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
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    stop)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/stop-postgres.sh"
        else
            echo "Error: Service not specified. Use -p for PostgreSQL service."
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
            echo "Error: Service not specified. Use -p for PostgreSQL service."
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
            echo "Error: Service not specified. Use -p for PostgreSQL service."
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
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    parser)
        if [ ${#ARGS[@]} -eq 0 ]; then
            echo "Error: Parser name or number not specified"
            show_help
            exit 1
        fi
        "$SCRIPT_DIR/bin/parser.sh" "${ARGS[@]}"
        ;;
    generate)
        if [ "$SERVICE" = "postgres" ]; then
            if [ ${#ARGS[@]} -eq 0 ]; then
                echo "Error: Generate type not specified"
                echo "Usage: $0 -p generate [init|migration]"
                exit 1
            fi
            case "${ARGS[0]}" in
                init)
                    echo "Generating initialization data..."
                    "$SCRIPT_DIR/bin/generate-init.sh"
                    ;;
                migration)
                    echo "Generating migration data..."
                    "$SCRIPT_DIR/bin/generate-migration.sh"
                    ;;
                *)
                    echo "Error: Unknown generate type '${ARGS[0]}'"
                    echo "Usage: $0 -p generate [init|migration]"
                    exit 1
                    ;;
            esac
        else
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    check)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/check-with-dev-db.sh"
        else
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    deploy)
        if [ "$SERVICE" = "postgres" ]; then
            "$SCRIPT_DIR/bin/deploy-migration.sh"
        else
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    *)
        echo "Error: Unknown command '$COMMAND'"
        show_help
        exit 1
        ;;
esac 