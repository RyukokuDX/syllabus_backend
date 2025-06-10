#!/bin/bash
# File Version: v1.0.1
# Project Version: v1.0.1
# Last Updated: 2024-03-19

# 現在バージョン
version=$(grep -oE '[0-9]+\.[0-9]+\.[0-9]+' version.txt | head -1)
IFS='.' read -r major minor patch <<< "$version"
next="$major.$minor.$((patch + 1))"
today=$(date +"%Y-%m-%d")

exts="\.md$|\.sh$|\.json$|\.py$"
target_files=$(git ls-files | grep -E "$exts")

declare -A file_versions  # key=ファイル名, value=旧バージョン

# バージョン文字列を置換し記録
for file in $target_files; do
  # ファイル拡張子に基づいてコメントアウト方法を決定
  case "$file" in
    *.md) 
      # Markdownファイルの場合、YAML Front Matterと箇条書き形式で更新
      if grep -q "file_version: v$version" "$file"; then
        # YAML Front Matterの更新
        sed -i "s/file_version: v$version/file_version: v$next/g" "$file"
        sed -i "s/project_version: v$version/project_version: v$next/g" "$file"
        sed -i "s/last_updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/last_updated: $today/g" "$file"
        
        # 箇条書き形式の更新
        sed -i "s/File Version: v$version/File Version: v$next/g" "$file"
        sed -i "s/Project Version: v$version/Project Version: v$next/g" "$file"
        sed -i "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $today/g" "$file"
        
        file_versions["$file"]="$version"
      fi
      ;;
    *.py|*.sh)
      # Python/Shellファイルの場合、#コメントで更新
      if grep -q "# File Version: v$version" "$file"; then
        sed -i "s/# File Version: v$version/# File Version: v$next/g" "$file"
        sed -i "s/# Project Version: v$version/# Project Version: v$next/g" "$file"
        sed -i "s/# Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/# Last Updated: $today/g" "$file"
        file_versions["$file"]="$version"
      fi
      ;;
    *.json)
      # JSONファイルの場合、//コメントで更新
      if grep -q "// File Version: v$version" "$file"; then
        sed -i "s/\/\/ File Version: v$version/\/\/ File Version: v$next/g" "$file"
        sed -i "s/\/\/ Project Version: v$version/\/\/ Project Version: v$next/g" "$file"
        sed -i "s/\/\/ Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/\/\/ Last Updated: $today/g" "$file"
        file_versions["$file"]="$version"
      fi
      ;;
  esac
done

# version.txtも追加
sed -i "s/$version/$next/" version.txt
file_versions["version.txt"]="$version"

# ステージ
git add "${!file_versions[@]}"

# コミットテンプレート作成（Markdown形式）
{
  echo "# bump time: $today"
  echo
  echo "# bump list"
  for f in "${!file_versions[@]}"; do
    echo "- $f: ${file_versions[$f]}"
  done
  echo
  echo "# bump summary"
  for f in "${!file_versions[@]}"; do
    echo "## $f"
    echo "- version: ${file_versions[$f]}"
    echo "- type: bump"
    echo "- summary: （ここに変更内容を記入）"
    echo
  done
} > commit_msg