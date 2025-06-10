#!/bin/bash
# File Version: v1.0.1
# Project Version: v1.0.1
# Last Updated: 2024-03-19

# 対象のMarkdownファイルを取得
md_files=$(git ls-files "*.md")

for file in $md_files; do
  echo "Processing $file..."
  
  # 現在のバージョン情報を取得
  file_version=$(grep -o "File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+" "$file" | head -1 | cut -d' ' -f3)
  project_version=$(grep -o "Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+" "$file" | head -1 | cut -d' ' -f3)
  last_updated=$(grep -o "Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$file" | head -1 | cut -d' ' -f3)
  
  if [ -z "$file_version" ] || [ -z "$project_version" ] || [ -z "$last_updated" ]; then
    echo "Warning: Could not find version information in $file"
    continue
  fi
  
  # タイトルを取得
  title=$(grep -m 1 "^# " "$file" | sed 's/^# //')
  
  # 一時ファイルを作成
  temp_file=$(mktemp)
  
  # YAML Front Matterを追加
  {
    echo "---"
    echo "title: $title"
    echo "file_version: $file_version"
    echo "project_version: $project_version"
    echo "last_updated: $last_updated"
    echo "---"
    echo
  } > "$temp_file"
  
  # 既存の内容を追加
  cat "$file" >> "$temp_file"
  
  # 一時ファイルを元のファイルに移動
  mv "$temp_file" "$file"
  
  echo "Successfully migrated $file"
done

echo "Migration completed!" 