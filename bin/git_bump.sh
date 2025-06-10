#!/bin/bash
# File Version: v1.0.7
# Project Version: v1.0.7
# Last Updated: 2025-06-10

# バージョン更新の種類を確認
if [ "$1" != "major" ] && [ "$1" != "minor" ] && [ "$1" != "patch" ]; then
  echo "Usage: git bump [major|minor|patch]"
  echo "  major: メジャーバージョンを更新（例：1.0.0 -> 2.0.0）"
  echo "  minor: マイナーバージョンを更新（例：1.0.0 -> 1.1.0）"
  echo "  patch: パッチバージョンを更新（例：1.0.0 -> 1.0.1）"
  exit 1
fi

# バージョン更新の種類を設定
BUMP_TYPE=$1

# 現在のプロジェクトバージョンを読み取り
CURRENT_VERSION=$(cat project_version.txt)
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# 次のバージョンを計算
case $BUMP_TYPE in
  "major")
    NEXT_MAJOR=$((MAJOR + 1))
    NEXT_MINOR=0
    NEXT_PATCH=0
    ;;
  "minor")
    NEXT_MAJOR=$MAJOR
    NEXT_MINOR=$((MINOR + 1))
    NEXT_PATCH=0
    ;;
  "patch")
    NEXT_MAJOR=$MAJOR
    NEXT_MINOR=$MINOR
    NEXT_PATCH=$((PATCH + 1))
    ;;
esac

NEXT_VERSION="$NEXT_MAJOR.$NEXT_MINOR.$NEXT_PATCH"
TODAY=$(date +%Y-%m-%d)

# 変更されたファイルを検出
CHANGED_FILES=$(git status --porcelain | grep -E '\.(md|py|sh|json)$' | awk '{print $2}')

# バージョン情報を持つファイルを特定
VERSION_FILES=()
for file in $CHANGED_FILES; do
  if grep -q "file_version:" "$file" || grep -q "File Version:" "$file"; then
    VERSION_FILES+=("$file")
  fi
done

# project_version.txtも追加
VERSION_FILES+=("project_version.txt")

# コミットメッセージのヘッダーを生成
echo "# bump time: $TODAY" > commit_msg
echo "" >> commit_msg
echo "# bump list" >> commit_msg

# 各ファイルのバージョンを更新し、コミットメッセージに追加
for file in "${VERSION_FILES[@]}"; do
  if [ -f "$file" ]; then
    # 現在のバージョンを取得
    CURRENT_FILE_VERSION=$(grep -E "file_version:|File Version:" "$file" | head -n 1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
    if [ -z "$CURRENT_FILE_VERSION" ]; then
      CURRENT_FILE_VERSION=$CURRENT_VERSION
    fi

    # コミットメッセージに追加
    echo "- $file: $CURRENT_FILE_VERSION" >> commit_msg

    # ファイルの種類に応じてバージョン情報を更新
    case "$file" in
      *.md)
        # Markdownファイルの更新
        sed -i "s/file_version: v[0-9]\+\.[0-9]\+\.[0-9]\+/file_version: v$NEXT_VERSION/" "$file"
        sed -i "s/project_version: v[0-9]\+\.[0-9]\+\.[0-9]\+/project_version: v$NEXT_VERSION/" "$file"
        sed -i "s/last_updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/last_updated: $TODAY/" "$file"
        sed -i "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/" "$file"
        ;;
      *.py|*.sh)
        # Python/Shellファイルの更新
        sed -i "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/" "$file"
        ;;
      *.json)
        # JSONファイルの更新
        sed -i "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/" "$file"
        sed -i "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/" "$file"
        ;;
      project_version.txt)
        # project_version.txtの更新
        echo "$NEXT_VERSION" > "$file"
        ;;
    esac
  fi
done

# コミットメッセージのサマリー部分を生成
echo "" >> commit_msg
echo "# bump summary" >> commit_msg

for file in "${VERSION_FILES[@]}"; do
  if [ -f "$file" ]; then
    CURRENT_FILE_VERSION=$(grep -E "file_version:|File Version:" "$file" | head -n 1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
    if [ -z "$CURRENT_FILE_VERSION" ]; then
      CURRENT_FILE_VERSION=$CURRENT_VERSION
    fi

    echo "## $file" >> commit_msg
    echo "- version: $CURRENT_FILE_VERSION" >> commit_msg
    echo "- type: $BUMP_TYPE bump" >> commit_msg
    echo "- summary: （ここに変更内容を記入）" >> commit_msg
    echo "" >> commit_msg
  fi
done

# 変更をステージング
git add "${VERSION_FILES[@]}"

echo "バージョンを $CURRENT_VERSION から $NEXT_VERSION に更新しました。"
echo "commit_msgを編集してからコミットしてください。"