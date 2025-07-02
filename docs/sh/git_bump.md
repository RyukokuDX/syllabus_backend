---
title: git_bump.sh
file_version: v2.3.0
project_version: v2.3.0
last_updated: 2025-07-02
---

# git_bump.sh

- File Version: v2.3.0
- Project Version: v2.3.0
- Last Updated: 2025-07-02

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md) | [Gitコミットポリシーへ](../git_commit_policy.md)

## 目次
1. [概要](#概要)
2. [機能](#機能)
3. [使用方法](#使用方法)
4. [バージョン更新の種類](#バージョン更新の種類)
5. [ファイル形式別の更新方法](#ファイル形式別の更新方法)
6. [コミットメッセージ](#コミットメッセージ)
7. [注意事項](#注意事項)

## 概要

`git_bump.sh`は、プロジェクトのバージョン管理を自動化するスクリプトです。セマンティックバージョニングに基づいて、プロジェクト全体と各ファイルのバージョンを更新します。

### 導入方法
1. スクリプトの配置
   ```bash
   # binディレクトリに配置
   cp git_bump.sh bin/
   chmod +x bin/git_bump.sh
   ```

2. Gitエイリアスの設定
   ```bash
   # プロジェクトの.git/configに追加
   git config alias.bump '!bin/git_bump.sh'
   ```

3. プロジェクトバージョンの初期化
   ```bash
   # project_version.txtを作成
   echo "1.0.0" > project_version.txt
   ```

### バージョン管理の特徴
- パッチレベル（X.Y.ZのZ）はファイルごとに独立
  - 各ファイルの変更に応じて個別に更新
  - 例：file1.mdが1.0.1、file2.mdが1.0.2など

- マイナー/メジャーレベル（X.YのY、X）はプロジェクト全体で統一
  - プロジェクトバージョンに連動
  - すべてのファイルが同じバージョンに更新
  - 例：プロジェクトが1.1.0になると、全ファイルも1.1.0に

### 目的
- バージョン更新の自動化
- 一貫性のあるバージョン管理
- コミットメッセージの自動生成

### 特徴
- メジャー・マイナー・パッチの3種類のバージョン更新に対応
- 複数のファイル形式に対応（Markdown, Python, Shell, JSON）
- バージョン情報の一括更新
- コミットメッセージの自動生成

## 機能

1. バージョン更新
   - プロジェクトバージョンの更新
   - 各ファイルのバージョン更新
   - 更新日時の自動更新

2. ファイル形式対応
   - Markdown: YAML Front Matterと箇条書き形式
   - Python/Shell: #コメント形式
   - JSON: //コメント形式

3. コミットメッセージ生成
   - 更新日時
   - 更新ファイル一覧
   - バージョン更新の種類
   - 変更内容の記入欄

## 使用方法

```bash
# パッチバージョンの更新（例：1.0.0 -> 1.0.1）
git bump patch

# マイナーバージョンの更新（例：1.0.0 -> 1.1.0）
git bump minor

# メジャーバージョンの更新（例：1.0.0 -> 2.0.0）
git bump major
```

## バージョン更新の種類

### メジャーバージョン（major）
- 後方互換性のない変更
- メジャーバージョンを+1
- マイナーとパッチを0にリセット
- 例：1.0.0 -> 2.0.0

### マイナーバージョン（minor）
- 後方互換性のある機能追加
- マイナーバージョンを+1
- パッチを0にリセット
- 例：1.0.0 -> 1.1.0

### パッチバージョン（patch）
- 後方互換性のあるバグ修正
- パッチバージョンのみ+1
- 例：1.0.0 -> 1.0.1

## ファイル形式別の更新方法

### Markdownファイル
```markdown
---
title: タイトル
file_version: v2.3.0
project_version: v2.3.0
last_updated: 2025-07-02
---

# タイトル

- File Version: v2.3.0
- Project Version: v2.3.0
- Last Updated: 2025-07-02
```

### Python/Shellファイル
```python
# File Version: v2.3.0
# Project Version: v2.3.0
# Last Updated: 2025-07-02
```

### JSONファイル
```json
// File Version: v2.3.0
// Project Version: v2.3.0
// Last Updated: 2025-07-02
```

## コミットメッセージ

### 形式
```markdown
# bump time: YYYY-MM-DD

# bump list
- ファイル名: 旧バージョン

# bump summary
## ファイル名
- version: 旧バージョン
- type: [major|minor|patch] bump
- summary: （ここに変更内容を記入）
```

### 例
```markdown
# bump time: 2024-03-20

# bump list
- project_version.txt: 1.0.0
- README.md: 1.0.0
- src/main.py: 1.0.0

# bump summary
## project_version.txt
- version: 1.0.0
- type: minor bump
- summary: マイナーバージョンを更新

## README.md
- version: 1.0.0
- type: minor bump
- summary: バージョン情報を更新

## src/main.py
- version: 1.0.0
- type: minor bump
- summary: バージョン情報を更新
```

## 注意事項

1. バージョン更新前の確認
   - 変更内容が適切なバージョン更新タイプか確認
   - コミットメッセージの内容を確認

2. ファイル形式の制限
   - 対応形式: .md, .py, .sh, .json
   - その他の形式は更新対象外

3. バージョン情報の形式
   - セマンティックバージョニング（X.Y.Z）に準拠
   - ファイルバージョンはプロジェクトバージョンに連動

4. コミットメッセージの編集
   - 生成されたコミットメッセージを確認
   - 変更内容を適切に記入

[🔝 ページトップへ](#git_bumpsh) 