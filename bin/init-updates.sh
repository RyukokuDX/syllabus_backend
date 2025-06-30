#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
UPDATES_DIR="$PROJECT_ROOT/updates"

# updatesディレクトリ内のすべてのサブディレクトリを取得
for dir in "$UPDATES_DIR"/*/; do
    if [ -d "$dir" ]; then
        add_dir="$dir/add"
        if [ -d "$add_dir" ]; then
            echo "Cleaning directory: $add_dir"
            rm -f "$add_dir"/*
            echo "All files in $add_dir have been removed."
        fi
    fi
done

echo -e "\nAll update directories have been cleaned." 