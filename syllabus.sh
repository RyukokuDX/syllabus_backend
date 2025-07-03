#!/bin/bash
# -*- coding: utf-8 -*-
# - 更新の登録は, /docs/version_control.md に準拠して実行
# File Version: 2.0.1
# Project Version: 2.0.1
# Last Update: 2025-07-01

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]:-$0}" )" && pwd )"
VENV_DIR="$SCRIPT_DIR/venv_syllabus_backend"
PYTHON="$VENV_DIR/bin/python"

# .envファイルのパスを設定
ENV_FILE="$SCRIPT_DIR/.env"



# OS別コマンド設定の読み込み
source "$SCRIPT_DIR/bin/os_utils.sh"
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
NC='\033[0m' # No Color

# ファイルの更新履歴を表示
show_file_history() {
    local file_path="$1"
    
    # バージョンディレクトリの取得（共通関数を使用）
    VERSION_DIRS=($(get_version_dirs "version" "v*"))
    
    if [[ ${#VERSION_DIRS[@]} -eq 0 ]]; then
        echo -e "${YELLOW}警告: バージョンディレクトリが見つかりません${NC}"
        exit 0
    fi
    
    # ファイルの更新履歴を表示
    echo -e "\n${GREEN}ファイル: $file_path の更新履歴${NC}"
    echo "=================================================="
    
    for version_dir in "${VERSION_DIRS[@]}"; do
        # docs/で始まるパスの場合は、そのまま使用
        json_file="${version_dir}/${file_path}.json"
        if [[ -f "$json_file" ]]; then
            # バージョン情報の取得
            version=$(jq -r '.meta_data.version' "$json_file")
            created_at=$(jq -r '.meta_data.created_at' "$json_file")
            
            echo -e "\n${YELLOW}バージョン: $version${NC}"
            echo -e "${YELLOW}作成日時: $created_at${NC}"
            echo "------------------------------"
            
            # 変更履歴の表示
            jq -r '.path_level | to_entries | sort_by(.key | tonumber) | .[] | 
                "レベル \(.key):\n  日時: \(.value.date)\n  概要: \(.value.summary)\n  詳細: \(.value.details)\n"' "$json_file"
        fi
    done
}

# スクリプトのバージョンを表示
show_script_version() {
    local script_json="$SCRIPT_DIR/version/v1.0/syllabus.sh.json"
    if [[ -f "$script_json" ]]; then
        version=$(jq -r '.meta_data.version' "$script_json")
        created_at=$(jq -r '.meta_data.created_at' "$script_json")
        
        echo -e "\n${GREEN}syllabus.sh のバージョン情報${NC}"
        echo "=================================================="
        echo -e "${YELLOW}バージョン: $version${NC}"
        echo -e "${YELLOW}作成日時: $created_at${NC}"
        echo "------------------------------"
        
        # 変更履歴の表示
        jq -r '.path_level | to_entries | sort_by(.key | tonumber) | .[] | 
            "レベル \(.key):\n  日時: \(.value.date)\n  概要: \(.value.summary)\n  詳細: \(.value.details)\n"' "$script_json"
    else
        echo -e "${YELLOW}警告: バージョン情報が見つかりません${NC}"
    fi
}

# CSVファイルの整形
normalize_csv() {
    local year="$1"
    local subdir="$2"
    local csv_dir="$SCRIPT_DIR/src/course_guide/$year/csv"
    
    # サブディレクトリが指定されている場合は、パスに追加
    if [ -n "$subdir" ]; then
        csv_dir="$csv_dir/$subdir"
    fi
    
    if [ ! -d "$csv_dir" ]; then
        echo "エラー: 指定された年度のCSVディレクトリが存在しません: $csv_dir"
        exit 1
    fi
    
    echo "$year年度のCSVファイルを整形中... (ディレクトリ: $csv_dir)"
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
from db.parser.utils import normalize_subject_name, normalize_faculty_name

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
        # 科目名フィールドと課程名フィールドのインデックスを特定
        subject_name_index = None
        course_name_index = None
        for i, header in enumerate(headers):
            if header.strip() == '科目名':
                subject_name_index = i
            elif header.strip() == '学部課程':
                course_name_index = i
        
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
        
        # 課程名フィールドを正規化（存在する場合）
        if course_name_index is not None and len(normalized_row) > course_name_index and normalized_row[course_name_index] != 'NULL':
            normalized_row[course_name_index] = normalize_faculty_name(normalized_row[course_name_index])
        
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
    echo "  -g, --git       Gitサービスでコマンドを実行"
    echo
    echo "対応OS:"
    echo "  - Linux (Ubuntu, CentOS, etc.)"
    echo "  - macOS (Darwin)"
    echo "  - Windows (WSL, Cygwin, MSYS2)"
    echo
    echo "コマンド:"
    echo "  help           このヘルプメッセージを表示"
    echo "  version        syllabus.shのバージョンを表示"
    echo "  version <file> 指定されたファイルの更新履歴を表示"
    echo "  venv init      Python仮想環境を初期化"
    echo "  start          指定されたサービスを開始"
    echo "  stop           指定されたサービスを停止"
    echo "  ps             サービスの状態を表示"
    echo "  logs           サービスのログを表示"
    echo "  shell          PostgreSQLサービスのシェルを開く"
    echo "  records        全テーブルのレコード数を表示"
    echo "  parser         指定されたテーブルのパーサースクリプトを実行"
    echo "  migration      マイグレーション関連のコマンド"
    echo "  csv normalize 指定年度のCSVファイルを整形（区切り文字をタブに、空白を削除、科目名・課程名を正規化）"
    echo "  cache generate   指定されたキャッシュを生成"
    echo "  cache delete     指定されたキャッシュを削除"
    echo "  cache refresh    指定されたキャッシュを削除して再生成"
    echo "  cache get full   全キャッシュデータを取得・整形"
    echo "  cache list       利用可能なキャッシュ一覧を表示"
    echo "  cache status     キャッシュの状態を表示"
    echo "  sql <sqlfile>    指定したSQLファイルをPostgreSQLサーバーで実行"
    echo "  update          minorバージョンアップをdevelopへマージ（squash/no-ff選択）"
    echo "  test-os           OS互換性テストを実行"
    echo
    echo "使用例:"
    echo "  $0 venv init             # Python仮想環境を初期化"
    echo "  $0 -p start              # PostgreSQLサービスを開始"
    echo "  $0 -p stop               # PostgreSQLサービスを停止"
    echo "  $0 -p shell              # PostgreSQLサービスのシェルを開く"
    echo "  $0 -p records            # レコード数を表示"
    echo "  $0 parser book           # 書籍パーサーを実行"
    echo "  $0 parser syllabus       # シラバスパーサーを実行"
    echo "  $0 parser instructor     # 教員パーサーを実行"
    echo "  $0 -p migration generate init      # 初期化データを生成"
    echo "  $0 -p migration generate migration # マイグレーションデータを生成"
    echo "  $0 -p migration check              # マイグレーションをチェック"
    echo "  $0 -p migration deploy             # マイグレーションをデプロイ"
    echo "  $0 csv normalize 2024    # 2024年度のCSVファイルを整形"
    echo "  $0 csv normalize 2025 Y  # 2025年度のYサブディレクトリのCSVファイルを整形"
    echo "  $0 -p cache generate subject_syllabus_cache  # 科目別シラバスキャッシュを生成"
    echo "  $0 -p cache delete subject_syllabus_cache    # 科目別シラバスキャッシュを削除"
    echo "  $0 -p cache refresh subject_syllabus_cache   # 科目別シラバスキャッシュを削除して再生成"
    echo "  $0 -p cache get full     # 全キャッシュデータを取得・整形"
    echo "  $0 -p cache list         # キャッシュ一覧を表示"
    echo "  $0 -p cache status       # キャッシュの状態を表示"
    echo "  $0 -p sql tests/cache_sample3.sql   # SQLファイルをPostgreSQLサーバーで実行"
    echo "  $0 update squash         # squashでdevelopにminorマージ"
    echo "  $0 update noff           # no-ffでdevelopにminorマージ"
    echo "  $0 test-os               # OS互換性テストを実行"
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
		-g|--git)
			SERVICE="git"
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

# サービスごとに許可コマンドを分岐
if [ "$SERVICE" = "git" ]; then
	case $COMMAND in
		update)
			if [ ${#ARGS[@]} -lt 2 ]; then
				echo "エラー: updateコマンドのサブコマンドが不足しています"
				echo "使用方法: $0 -g update minor <squash|noff>"
				exit 1
			fi
			if [ "${ARGS[0]}" = "minor" ]; then
				if [ "${ARGS[1]}" != "squash" ] && [ "${ARGS[1]}" != "noff" ]; then
					echo "エラー: squash か noff を指定してください"
					exit 1
				fi
				"$SCRIPT_DIR/bin/minor_version_update.sh" "${ARGS[1]}"
			else
				echo "エラー: minor以外は未対応です"
				exit 1
			fi
			;;
		*)
			echo "エラー: git関連で許可されていないコマンドです: $COMMAND"
			show_help
			exit 1
			;;
	esac
	# gitサービスの場合はここで終了
	exit 0
fi

if [ "$SERVICE" = "postgres" ]; then
	# コマンドの実行
	case $COMMAND in
		help)
			show_help
			;;
		version)
			if [ ${#ARGS[@]} -eq 0 ]; then
				show_script_version
			else
				show_file_history "${ARGS[0]}"
			fi
			;;
		venv)
			if [ ${#ARGS[@]} -eq 0 ]; then
				echo "エラー: venvコマンドのサブコマンドが指定されていません"
				echo "使用方法: $0 venv [init]"
				exit 1
			fi
			case "${ARGS[0]}" in
				init)
					init_venv
					;;
				*)
					echo "エラー: 不明なvenvコマンド '${ARGS[0]}'"
					echo "使用方法: $0 venv [init]"
					exit 1
					;;
			esac
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
						echo "使用方法: $0 csv normalize <year> [subdir]"
						exit 1
					fi
					# サブディレクトリが指定されている場合は3番目の引数、そうでなければ空文字列
					subdir=""
					if [ ${#ARGS[@]} -ge 3 ]; then
						subdir="${ARGS[2]}"
					fi
					normalize_csv "${ARGS[1]}" "$subdir"
					;;
				*)
					echo "エラー: 不明なCSVコマンド '${ARGS[0]}'"
					show_help
					exit 1
					;;
			esac
			;;
		start)
			"$SCRIPT_DIR/bin/start-postgres.sh"
			;;
		stop)
			"$SCRIPT_DIR/bin/stop-postgres.sh"
			;;
		restart)
			"$SCRIPT_DIR/bin/stop-postgres.sh"
			"$SCRIPT_DIR/bin/start-postgres.sh"
			;;
		ps)
			docker ps
			;;
		logs)
			docker logs -f postgres-db
			;;
		shell)
			# .envファイルからデータベース名とユーザー名を取得
			DB_NAME=$(get_env_value "POSTGRES_DB" "$ENV_FILE")
			DB_USER=$(get_env_value "POSTGRES_USER" "$ENV_FILE")
			docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME"
			;;
		records)
			if [ ${#ARGS[@]} -eq 0 ]; then
				# 引数なし: 従来通り全テーブルの件数表示
				DB_NAME=$(get_env_value "POSTGRES_DB" "$ENV_FILE")
				DB_USER=$(get_env_value "POSTGRES_USER" "$ENV_FILE")
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
				DB_NAME=$(get_env_value "POSTGRES_DB" "$ENV_FILE")
				DB_USER=$(get_env_value "POSTGRES_USER" "$ENV_FILE")
				docker exec postgres-db psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT * FROM $TABLE_NAME;"
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
		migration)
			if [ ${#ARGS[@]} -eq 0 ]; then
				echo "エラー: マイグレーションコマンドのサブコマンドが指定されていません"
				echo "使用方法: $0 -p migration [generate|check|deploy] [init|migration]"
				exit 1
			fi
			case "${ARGS[0]}" in
				generate)
					if [ ${#ARGS[@]} -lt 2 ]; then
						echo "エラー: 生成タイプが指定されていません"
						echo "使用方法: $0 -p migration generate [init|migration]"
						exit 1
					fi
					case "${ARGS[1]}" in
						init)
							echo "初期化データを生成中..."
							"$SCRIPT_DIR/bin/generate-init.sh"
							;;
						migration)
							echo "マイグレーションデータを生成中..."
							"$SCRIPT_DIR/bin/generate-migration.sh"
							;;
						*)
							echo "エラー: 不明な生成タイプ '${ARGS[1]}'"
							echo "使用方法: $0 -p migration generate [init|migration]"
							exit 1
							;;
					esac
					;;
				check)
					"$SCRIPT_DIR/bin/check-with-dev-db.sh"
					;;
				deploy)
					"$SCRIPT_DIR/bin/deploy-migration.sh"
					;;
				*)
					echo "エラー: 不明なマイグレーションコマンド '${ARGS[0]}'"
					echo "使用方法: $0 -p migration [generate|check|deploy] [init|migration]"
					exit 1
					;;
			esac
			;;
		cache)
			if [ ${#ARGS[@]} -eq 0 ]; then
				echo "エラー: キャッシュコマンドのサブコマンドが指定されていません"
				echo "使用方法: $0 -p cache [generate|delete|list|status] [cache_name]"
				exit 1
			fi
			case "${ARGS[0]}" in
				generate)
					if [ ${#ARGS[@]} -lt 2 ]; then
						echo "エラー: キャッシュ名が指定されていません"
						echo "使用方法: $0 -p cache generate <cache_name>"
						exit 1
					fi
					"$SCRIPT_DIR/bin/json_cache.sh" generate "${ARGS[1]}"
					;;
				delete)
					if [ ${#ARGS[@]} -lt 2 ]; then
						echo "エラー: キャッシュ名が指定されていません"
						echo "使用方法: $0 -p cache delete <cache_name>"
						exit 1
					fi
					"$SCRIPT_DIR/bin/json_cache.sh" delete "${ARGS[1]}"
					;;
				refresh)
					if [ ${#ARGS[@]} -lt 2 ]; then
						echo "エラー: キャッシュ名が指定されていません"
						echo "使用方法: $0 -p cache refresh <cache_name>"
						exit 1
					fi
					"$SCRIPT_DIR/bin/json_cache.sh" refresh "${ARGS[1]}"
					;;
				get)
					if [ ${#ARGS[@]} -lt 2 ]; then
						echo "エラー: 取得タイプが指定されていません"
						echo "使用方法: $0 -p cache get [full]"
						exit 1
					fi
					case "${ARGS[1]}" in
						full)
							"$SCRIPT_DIR/bin/get_cache.sh" full
							;;
						*)
							echo "エラー: 不明な取得タイプ '${ARGS[1]}'"
							echo "使用方法: $0 -p cache get [full]"
							exit 1
							;;
					esac
					;;
				list)
					"$SCRIPT_DIR/bin/json_cache.sh" list
					;;
				status)
					"$SCRIPT_DIR/bin/json_cache.sh" status
					;;
				*)
					echo "エラー: 不明なキャッシュコマンド '${ARGS[0]}'"
					echo "使用方法: $0 -p cache [generate|delete|refresh|get|list|status] [cache_name|full]"
					exit 1
					;;
			esac
			;;
		sql)
			if [ ${#ARGS[@]} -eq 0 ]; then
				echo "エラー: SQLファイルが指定されていません"
				echo "使用方法: $0 -p sql <sqlfile>"
				exit 1
			fi
			
			sql_file="${ARGS[0]}"
			if [ ! -f "$sql_file" ]; then
				echo "エラー: SQLファイルが見つかりません: $sql_file"
				exit 1
			fi
			
			echo "SQLファイルを実行中: $sql_file"
			DB_NAME=$(get_env_value "POSTGRES_DB" "$ENV_FILE")
			DB_USER=$(get_env_value "POSTGRES_USER" "$ENV_FILE")
			docker exec -i postgres-db psql -U "$DB_USER" -d "$DB_NAME" < "$sql_file"
			;;
		test-os)
			"$SCRIPT_DIR/bin/test_os_compatibility.sh"
			;;
		*)
			echo "エラー: 不明なコマンド '$COMMAND'"
			show_help
			exit 1
			;;
	esac
else
	# それ以外（共通コマンド）
	case $COMMAND in
		help)
			show_help
			;;
		version)
			if [ ${#ARGS[@]} -eq 0 ]; then
				show_script_version
			else
				show_file_history "${ARGS[0]}"
			fi
			;;
		venv)
			if [ ${#ARGS[@]} -eq 0 ]; then
				echo "エラー: venvコマンドのサブコマンドが指定されていません"
				echo "使用方法: $0 venv [init]"
				exit 1
			fi
			case "${ARGS[0]}" in
				init)
					init_venv
					;;
				*)
					echo "エラー: 不明なvenvコマンド '${ARGS[0]}'"
					echo "使用方法: $0 venv [init]"
					exit 1
					;;
			esac
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
						echo "使用方法: $0 csv normalize <year> [subdir]"
						exit 1
					fi
					# サブディレクトリが指定されている場合は3番目の引数、そうでなければ空文字列
					subdir=""
					if [ ${#ARGS[@]} -ge 3 ]; then
						subdir="${ARGS[2]}"
					fi
					normalize_csv "${ARGS[1]}" "$subdir"
					;;
				*)
					echo "エラー: 不明なCSVコマンド '${ARGS[0]}'"
					show_help
					exit 1
					;;
			esac
			;;
		test-os)
			"$SCRIPT_DIR/bin/test_os_compatibility.sh"
			;;
		*)
			echo "エラー: 不明なコマンド '$COMMAND'"
			show_help
			exit 1
			;;
	esac
fi 