#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/syllabus_backend_venv"
PYTHON="$VENV_DIR/bin/python"

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
    "$PYTHON" -m pip install --upgrade pip
    "$PYTHON" -m pip install -r "$SCRIPT_DIR/requirements.txt"
    
    echo "Virtual environment initialized successfully"
}

# ヘルプメッセージを表示
show_help() {
    echo "Usage: $0 [OPTIONS] COMMAND [ARGS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -p, --postgres Run command in PostgreSQL service"
    echo
    echo "Commands:"
    echo "  help           Show this help message"
    echo "  venv-init      Initialize Python virtual environment"
    echo "  up             Start all services"
    echo "  down           Stop all services"
    echo "  ps             Show service status"
    echo "  logs           Show service logs"
    echo "  shell          Open shell in PostgreSQL service"
    echo "  records        Show record counts for all tables"
    echo "  parser         Run parser script for specified table"
    echo
    echo "Examples:"
    echo "  $0 venv-init             # Initialize Python virtual environment"
    echo "  $0 up                    # Start all services"
    echo "  $0 -p shell              # Open shell in PostgreSQL service"
    echo "  $0 -p records            # Show record counts"
    echo "  $0 parser book           # Run book parser"
    echo "  $0 parser syllabus       # Run syllabus parser"
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
        -p|--postgres)
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
    up)
        docker-compose up -d
        ;;
    down)
        docker-compose down
        ;;
    ps)
        docker-compose ps
        ;;
    logs)
        docker-compose logs -f
        ;;
    shell)
        if [ "$SERVICE" = "postgres" ]; then
            docker-compose exec postgres psql -U postgres -d syllabus
        else
            echo "Error: Service not specified. Use -p for PostgreSQL service."
            exit 1
        fi
        ;;
    records)
        if [ "$SERVICE" = "postgres" ]; then
            docker-compose exec postgres psql -U postgres -d syllabus -c "
                SELECT 
                    schemaname || '.' || relname as table_name,
                    n_live_tup as record_count
                FROM pg_stat_user_tables
                ORDER BY relname;
            "
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
    *)
        echo "Error: Unknown command '$COMMAND'"
        show_help
        exit 1
        ;;
esac 