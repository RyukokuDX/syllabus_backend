---
title: Gitコミットポリシー
file_version: v1.0.2
project_version: v1.0.2
last_updated: 2025-06-10
---

# Gitコミットポリシー

- File Version: v1.0.2
- Project Version: v1.0.2
- Last Updated: 2025-06-10

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](./doc.md)

## 目次
1. [基本方針](#基本方針)
2. [コミットメッセージ](#コミットメッセージ)
3. [ブランチ管理](#ブランチ管理)
4. [バージョン管理](#バージョン管理)
5. [アップデートのコミット方法](#アップデートのコミット方法)
6. [マージ戦略](#マージ戦略)

## 基本方針

### 文書の目的
- 開発者が一貫した方法でGitを運用できること
- 変更履歴が明確に追跡できること
- チーム内でのコミュニケーションが円滑であること

### 対象読者
- プロジェクトの開発者
- コードレビュアー
- プロジェクト管理者

## コミットメッセージ

### 基本形式
- 変更内容を明確に記述
- 例：「fix: ログインエラーを修正」「feat: ユーザー登録機能を追加」

### プレフィックス
- `feat:` - 新機能
- `fix:` - バグ修正
- `docs:` - ドキュメントの変更
- `style:` - コードの意味に影響を与えない変更
- `refactor:` - バグ修正や機能追加を含まないコードの変更
- `test:` - テストの追加・修正
- `chore:` - ビルドプロセスやツールの変更

### コミットメッセージの例
1. **通常のコミットメッセージ**
   ```
   docs: cursor.mdのコメントアウト内容を更新し、ファイル作成時の注意事項を追加。不要なPowerShellスクリプトとディレクトリ初期化スクリプトを削除。
   ```

2. **推奨されるコミットメッセージ形式**
   ```
   docs: cursor.mdの更新 (v1.0.1)

   Changes by file:
   docs/cursor.md (v1.0.1)
   - docs: コメントアウト内容を更新
   - docs: ファイル作成時の注意事項を追加

   scripts/init.ps1 (v1.0.1)
   - chore: PowerShellスクリプトを削除

   scripts/init.sh (v1.0.1)
   - chore: ディレクトリ初期化スクリプトを削除

   Details:
   - ファイル作成時の注意事項を明確化
   - 不要なスクリプトを整理
   ```

## ブランチ管理

### ブランチ命名規則
- 機能開発: `feature/機能名`
- バグ修正: `bugfix/修正内容`
- パッチ: `patch/修正内容`

### ブランチ運用
- 機能開発は feature/機能名 ブランチで実施
- パッチレベルの更新は個別ブランチで管理
- ブランチは目的を達成したら削除

## バージョン管理

### セマンティックバージョニング
- メジャー.マイナー.パッチ形式を採用
- 例：1.0.1, 1.1.0, 1.1.1

### タグ管理
- リリース時はタグを付与（例：v1.0.1）
- ファイルごとのバージョン管理もタグで実施
  - 例：docs/version_control.md@v1.0.1
  - コミットメッセージにファイルのバージョン情報を含める

### ブランチ運用
- developブランチには minor と major の更新のみをプッシュ
- パッチレベルの更新は個別ブランチで管理

## アップデートのコミット方法

### patch level（ブランチでの作業）
- 個別の修正や小さな変更をコミット
- コミットメッセージ例：「fix: ログインエラーを修正」

### minor/major update（developへのマージ時）
- patch levelのコミットをsquashして1つのコミットにまとめる
- マージコミットメッセージでバージョンアップを明示
- 例：「feat: ユーザー認証システムの改善 (v1.1.0)」
- 変更内容の詳細をマージコミットメッセージに記載

## マージ戦略

### patch levelの修正履歴の保持方法
1. **通常のマージを使用**
   - `git merge --no-ff` を使用してマージコミットを作成
   - 個別のpatchレベルのコミット履歴が保持される
   - 例：
     ```bash
     git checkout develop
     git merge --no-ff feature/patch-updates
     ```

2. **マージコミットメッセージの活用**
   - マージコミットメッセージに変更内容を詳細に記載
   - 個別のpatchレベルのコミットハッシュを参照
   - 例：
     ```
     Merge patch updates (v1.0.1)

     - ログインエラー修正 (abc1234)
     - パフォーマンス改善 (def5678)
     - ドキュメント更新 (ghi9012)
     ```

3. **タグの活用**
   - 重要なpatchレベルの修正にタグを付与
   - 例：`v1.0.1-patch1`, `v1.0.1-patch2`
   - タグメッセージに修正内容を記載

### コミットメッセージへのpatch levelリストの追加方法
1. **マージ時のコミットメッセージ作成**
   ```bash
   # コミットメッセージを一時ファイルに保存
   git log feature/patch-updates --oneline > /tmp/commit-messages.txt
   
   # マージを実行（エディタでコミットメッセージを編集）
   git merge --no-ff feature/patch-updates
   ```

2. **コミットメッセージの形式**
   ```
   Merge patch updates (v1.0.1)

   Changes by file:
   docs/version_control.md (v1.0.1)
   - fix: ログインエラーを修正 (abc1234)
   - docs: API仕様書を更新 (ghi9012)

   src/auth/login.py (v1.0.1)
   - fix: バリデーション処理を修正 (def5678)
   - perf: クエリを最適化 (jkl3456)

   Details:
   - ログイン時のバリデーション処理を修正
   - インデックスを追加してクエリを最適化
   - 新規エンドポイントの説明を追加
   ```

3. **自動化スクリプトの例**
   ```bash
   #!/bin/bash
   BRANCH=$1
   VERSION=$2
   
   # ファイルごとのコミットメッセージを取得
   FILES=$(git diff --name-only develop...$BRANCH)
   for file in $FILES; do
     echo "$file ($VERSION)"
     git log $BRANCH --oneline -- "$file"
     echo
   done > /tmp/commit-messages.txt
   
   # マージを実行
   git merge --no-ff $BRANCH -m "Merge patch updates ($VERSION)

   Changes by file:
   $(cat /tmp/commit-messages.txt)"
   ```

### 推奨される運用
- パッチレベルの修正は個別のブランチで管理
- 修正が完了したら`--no-ff`オプションでマージ
- マージコミットメッセージに変更内容を詳細に記載
- 必要に応じてタグを付与
- コミットメッセージには変更の詳細な説明を含める
- ファイルごとに変更内容をまとめて記載
- 複数のファイルを変更する場合は、ファイルごとの変更内容を明確に記載

### ファイル更新時のバージョン管理
- ファイルを更新する際は、ファイル形式に応じて以下の形式でバージョン情報を記載します：

  **Markdownファイルの場合：**
  ```markdown
  ---
  title: タイトル
  file_version: v1.0.2
  project_version: v1.0.2
  last_updated: YYYY-MM-DD
  ---

  # タイトル

  - File Version: v1.0.2
  - Project Version: v1.0.2
  - Last Updated: YYYY-MM-DD
  ```

  **Pythonファイルの場合：**
  ```python
  # File Version: v1.0.2
  # Project Version: v1.0.2
  # Last Updated: YYYY-MM-DD
  ```

  **Shellスクリプトの場合：**
  ```bash
  # File Version: v1.0.2
  # Project Version: v1.0.2
  # Last Updated: YYYY-MM-DD
  ```

  **JSONファイルの場合：**
  ```json
  // File Version: v1.0.2
  // Project Version: v1.0.2
  // Last Updated: YYYY-MM-DD
  ```

- バージョン情報の更新は`git_bump.sh`によって自動的に行われます
- 更新時は`git_bump.sh`を実行し、生成されたコミットメッセージの「(ここに変更内容を記入)」の部分を、ファイル内容の変更から適切な内容に更新します
- 変更内容は箇条書きで詳細を記載します

### Cursorの挿入問題対策
1. **テンプレートファイルの作成**
   - 各ファイル形式用のテンプレートファイルを作成し、バージョン情報を含める
   - 例：`templates/python_template.py`, `templates/shell_template.sh`など

2. **VSCodeスニペットの活用**
   - 各ファイル形式用のスニペットを作成
   - 例：
     ```json
     {
       "Markdown File Header": {
         "prefix": "mdheader",
         "body": [
           "# $1",
           "",
           "- File Version: v1.0.2",
           "- Project Version: v1.0.2",
           "- Last Updated: $CURRENT_YEAR-$CURRENT_MONTH-$CURRENT_DATE"
         ]
       }
     }
     ```

3. **git_bump.shの拡張**
   - ファイル形式を検出し、適切なコメントアウト方法を適用する機能を追加
   - 例：
     ```bash
     # ファイル拡張子に基づいてコメントアウト方法を決定
     case "$file" in
       *.py) comment_prefix="#" ;;
       *.sh) comment_prefix="#" ;;
       *.json) comment_prefix="//" ;;
       *.md) comment_prefix="-" ;;
       *) comment_prefix="#" ;;
     esac
     ```

4. **CI/CDでの検証**
   - バージョン情報の形式が正しいことを確認するチェックを追加
   - 不正な形式の場合はエラーを報告

5. **ドキュメントの整備**
   - 各ファイル形式での正しいバージョン情報の記載方法を明確に文書化
   - チーム内で共有し、統一された形式を維持

### タグ運用方法

- バージョン管理にはgitのタグ機能を活用します。
- リリース時や重要な変更時には、下記のコマンドでタグを付与します。

#### タグの付与方法
```bash
# 例：v1.0.1というタグを付与
git tag v1.0.1

# 署名付きタグの場合
git tag -s v1.0.1 -m "リリースv1.0.1"
```

#### タグの確認・削除・push
```bash
# タグ一覧表示
git tag

# タグの詳細表示
git show v1.0.1

# タグの削除
git tag -d v1.0.1

# リモートにタグをpush
git push origin v1.0.1

# すべてのタグをリモートにpush
git push origin --tags
```

- タグにはセマンティックバージョニング（例：v1.0.1）を使用します。
- ファイル単位のバージョン管理が必要な場合は、`ファイル名@バージョン` の形式でタグを付与しても良いです（例：docs/version_control.md@v1.0.1）。

[🔝 ページトップへ](#gitコミットポリシー) 