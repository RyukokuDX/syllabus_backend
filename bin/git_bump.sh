#!/bin/bash
# File Version: v2.5.0
# Project Version: v2.5.0
# Last Updated: 2025-07-03

# スクリプトの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# OS別コマンド設定の読み込み
source "$SCRIPT_DIR/os_utils.sh"
OS_TYPE=$(init_os_commands)

# デバッグ用: SED_CMDの値を確認
echo "DEBUG: SED_CMD = '$SED_CMD'"
echo "DEBUG: OS_TYPE = '$OS_TYPE'"

# SED_CMDが空の場合はフォールバック
if [ -z "$SED_CMD" ]; then
    echo "WARNING: SED_CMD is empty, using fallback"
    OS_TYPE=$(uname -s)
    if [[ "$OS_TYPE" == "Darwin"* ]]; then
        SED_CMD="sed -i ''"
    else
        SED_CMD="sed -i"
    fi
    echo "DEBUG: Fallback SED_CMD = '$SED_CMD'"
fi

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

# デバッグ情報の出力
echo "Current version: $CURRENT_VERSION"
echo "Bump type: $BUMP_TYPE"
echo "Next version: $NEXT_VERSION"

# バージョン情報を持つファイルを検出
if [ "$BUMP_TYPE" = "minor" ] || [ "$BUMP_TYPE" = "major" ]; then
  # マイナー/メジャー更新時は全ファイルを対象
  VERSION_FILES=($(git ls-files | grep -E '\.(md|py|sh|json)$'))
else
  # パッチ更新時は変更されたファイルのみを対象
  VERSION_FILES=($(git diff --name-only HEAD | grep -E '\.(md|py|sh|json)$'))
fi

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
        if [ "$BUMP_TYPE" = "patch" ]; then
          # パッチ更新時はファイルごとのバージョンを更新
          IFS='.' read -r F_MAJOR F_MINOR F_PATCH <<< "$CURRENT_FILE_VERSION"
          NEXT_FILE_VERSION="$F_MAJOR.$F_MINOR.$((F_PATCH + 1))"
        else
          NEXT_FILE_VERSION=$NEXT_VERSION
        fi
        $SED_CMD "s/file_version: v[0-9]\+\.[0-9]\+\.[0-9]\+/file_version: v$NEXT_FILE_VERSION/g" "$file"
        $SED_CMD "s/project_version: v[0-9]\+\.[0-9]\+\.[0-9]\+/project_version: v$NEXT_VERSION/g" "$file"
        $SED_CMD "s/last_updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/last_updated: $TODAY/g" "$file"
        $SED_CMD "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_FILE_VERSION/g" "$file"
        $SED_CMD "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/g" "$file"
        $SED_CMD "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/g" "$file"
        ;;
      *.py|*.sh)
        # Python/Shellファイルの更新
        if [ "$BUMP_TYPE" = "patch" ]; then
          # パッチ更新時はファイルごとのバージョンを更新
          IFS='.' read -r F_MAJOR F_MINOR F_PATCH <<< "$CURRENT_FILE_VERSION"
          NEXT_FILE_VERSION="$F_MAJOR.$F_MINOR.$((F_PATCH + 1))"
        else
          NEXT_FILE_VERSION=$NEXT_VERSION
        fi
        $SED_CMD "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_FILE_VERSION/g" "$file"
        $SED_CMD "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/g" "$file"
        $SED_CMD "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/g" "$file"
        ;;
      *.json)
        # JSONファイルの更新
        if [ "$BUMP_TYPE" = "patch" ]; then
          # パッチ更新時はファイルごとのバージョンを更新
          IFS='.' read -r F_MAJOR F_MINOR F_PATCH <<< "$CURRENT_FILE_VERSION"
          NEXT_FILE_VERSION="$F_MAJOR.$F_MINOR.$((F_PATCH + 1))"
        else
          NEXT_FILE_VERSION=$NEXT_VERSION
        fi
        $SED_CMD "s/File Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/File Version: v$NEXT_FILE_VERSION/g" "$file"
        $SED_CMD "s/Project Version: v[0-9]\+\.[0-9]\+\.[0-9]\+/Project Version: v$NEXT_VERSION/g" "$file"
        $SED_CMD "s/Last Updated: [0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/Last Updated: $TODAY/g" "$file"
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
    if [ "$BUMP_TYPE" = "patch" ]; then
      # パッチ更新時はファイルごとのバージョンを更新
      IFS='.' read -r F_MAJOR F_MINOR F_PATCH <<< "$CURRENT_FILE_VERSION"
      NEXT_FILE_VERSION="$F_MAJOR.$F_MINOR.$((F_PATCH + 1))"
      echo "- version: $NEXT_FILE_VERSION" >> commit_msg
      echo "- type: $BUMP_TYPE bump" >> commit_msg
    else
      echo "- version: $NEXT_VERSION" >> commit_msg
      echo "- type: $BUMP_TYPE bump" >> commit_msg
    fi
    echo "- summary: （ここに変更内容を記入）" >> commit_msg
    echo "" >> commit_msg
  fi
done

# 変更をステージング
git add "${VERSION_FILES[@]}"

echo "バージョンを $CURRENT_VERSION から $NEXT_VERSION に更新しました。"
echo "commit_msgを編集してからコミットしてください。"