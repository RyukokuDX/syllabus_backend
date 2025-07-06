#!/bin/bash
# File Version: v2.7.0
# Project Version: v2.7.0
# Last Updated: 2025-07-06

# minor update用のシェルスクリプト
# 現在のブランチをdevelopにsquash/no-ffでマージ

set -e  # エラー時に終了

# 引数チェック
if [ $# -ne 1 ]; then
    echo "Usage: $0 <squash|noff>"
    echo "  squash: squash merge"
    echo "  noff: no-fast-forward merge"
    exit 1
fi

MERGE_TYPE=$1

# マージタイプの検証
if [ "$MERGE_TYPE" != "squash" ] && [ "$MERGE_TYPE" != "noff" ]; then
    echo "Error: Invalid merge type. Use 'squash' or 'noff'"
    exit 1
fi

# 現在のブランチ名を取得
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# developブランチに切り替え
echo "Switching to develop branch..."
git checkout develop

# developブランチを最新に更新
echo "Pulling latest changes from develop..."
git pull origin develop

# マージタイプに応じてマージ実行
if [ "$MERGE_TYPE" = "squash" ]; then
    echo "Performing squash merge..."
    git merge --squash "$CURRENT_BRANCH"
    
    # squash mergeの場合は、コンフリクト解決後にコミット
    echo "Resolving conflicts with --theirs..."
    git checkout --theirs .
    git add .
    
    echo "Committing squash merge..."
    git commit -m "feat: squash merge from $CURRENT_BRANCH\n\n- Minor version update\n- Squash merge completed"
    
elif [ "$MERGE_TYPE" = "noff" ]; then
    echo "Performing no-fast-forward merge..."
    git merge --no-ff "$CURRENT_BRANCH"
    
    # no-ff mergeでコンフリクトが発生した場合の処理
    if [ $? -ne 0 ]; then
        echo "Conflicts detected. Resolving with --theirs..."
        git checkout --theirs .
        git add .
        git commit -m "feat: no-ff merge from $CURRENT_BRANCH\n\n- Minor version update\n- No-fast-forward merge completed"
    fi
fi

echo "Merge completed successfully!"
echo "Current branch: $(git branch --show-current)"
echo "Ready to push to remote develop branch" 