#!/bin/bash

# スクリプトのディレクトリを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
UPDATES_DIR="$PROJECT_ROOT/updates"

# 作成するディレクトリのリスト
directories=(
    "class/add"
    "subclass/add"
    "class_note/add"
    "subject_name/add"
    "subject/add"
    "faculty/add"
    "instructor/add"
    "criteria/add"
    "book/add"
    "syllabus/add"
    "syllabus_faculty_enrollment/add"
    "lecture_session/add"
    "syllabus_instructor/add"
    "syllabus_book/add"
    "grading_criterion/add"
)

# 各ディレクトリを作成
for dir in "${directories[@]}"; do
    path="$UPDATES_DIR/$dir"
    if [ ! -d "$path" ]; then
        mkdir -p "$path"
        echo "Created directory: $path"
    else
        echo "Directory already exists: $path"
    fi
done

echo -e "\nAll directories have been created." 