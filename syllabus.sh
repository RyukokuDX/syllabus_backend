#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BIN_DIR="$SCRIPT_DIR/bin"

# ヘルプメッセージを表示
show_help() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo
    echo "Options:"
    echo "  -p, --postgresql      PostgreSQL service (default)"
    echo "  -a, --api            FastAPI service"
    echo "  -h, --help           Show this help message"
    echo
    echo "Commands:"
    echo "  start                Start the specified service"
    echo "  stop                 Stop the specified service"
    echo "  check                Check migrations with development database (PostgreSQL only)"
    echo "  deploy               Deploy migrations (PostgreSQL only)"
    echo "  generate             Generate migration files (PostgreSQL only)"
    echo "  init-dirs           Initialize update directories (PostgreSQL only)"
    echo "  clean                Clean update directories (PostgreSQL only)"
    echo
    echo "Examples:"
    echo "  $0 -p start          # Start PostgreSQL (required before check/deploy)"
    echo "  $0 -p check          # Check PostgreSQL migrations (requires PostgreSQL to be running)"
    echo "  $0 -p deploy         # Deploy migrations (requires PostgreSQL to be running)"
    echo "  $0 -a start          # Start FastAPI"
    echo
    echo "Note: For PostgreSQL operations, make sure to start the service first"
    echo "      using 'start' command before running 'check' or 'deploy'"
}

# デフォルトのサービス
SERVICE="postgresql"

# コマンドライン引数の解析
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--postgresql)
            SERVICE="postgresql"
            shift
            ;;
        -a|--api)
            SERVICE="api"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            COMMAND="$1"
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
case "$SERVICE" in
    postgresql)
        case "$COMMAND" in
            start)
                "$BIN_DIR/start-postgres.sh"
                ;;
            stop)
                "$BIN_DIR/stop-postgres.sh"
                ;;
            check)
                # PostgreSQLが起動しているか確認
                if ! docker-compose -f "$SCRIPT_DIR/docker/postgresql/docker-compose.yml" ps | grep -q "postgres-db.*Up"; then
                    echo "Error: PostgreSQL is not running. Please start it first using:"
                    echo "  $0 -p start"
                    exit 1
                fi
                "$BIN_DIR/check-with-dev-db.sh"
                ;;
            deploy)
                # PostgreSQLが起動しているか確認
                if ! docker-compose -f "$SCRIPT_DIR/docker/postgresql/docker-compose.yml" ps | grep -q "postgres-db.*Up"; then
                    echo "Error: PostgreSQL is not running. Please start it first using:"
                    echo "  $0 -p start"
                    exit 1
                fi
                "$BIN_DIR/deploy-migration.sh"
                ;;
            generate)
                "$BIN_DIR/generate-migration.sh"
                ;;
            init-dirs)
                "$BIN_DIR/init-directories.sh"
                ;;
            clean)
                "$BIN_DIR/init-updates.sh"
                ;;
            *)
                echo "Error: Unknown command '$COMMAND' for PostgreSQL service"
                show_help
                exit 1
                ;;
        esac
        ;;
    api)
        case "$COMMAND" in
            start)
                echo "Starting FastAPI service..."
                cd "$SCRIPT_DIR" || exit
                uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
                ;;
            stop)
                echo "Stopping FastAPI service..."
                pkill -f "uvicorn src.main:app"
                ;;
            *)
                echo "Error: Unknown command '$COMMAND' for API service"
                show_help
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Error: Unknown service '$SERVICE'"
        show_help
        exit 1
        ;;
esac 