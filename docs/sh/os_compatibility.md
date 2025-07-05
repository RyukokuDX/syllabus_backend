---
title: OS互換性
file_version: v2.6.0
project_version: v2.6.0
last_updated: 2025-07-05
---

# OS互換性

- File Version: v2.6.0
- Project Version: v2.6.0
- Last Updated: 2025-07-05

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md)

シラバスバックエンドシステムのマルチプラットフォーム対応について説明します。

## 目次
1. [概要](#概要)
2. [対応OS](#対応os)
3. [自動判別機能](#自動判別機能)
4. [OS別コマンド設定](#os別コマンド設定)
5. [共通ユーティリティ](#共通ユーティリティ)
6. [互換性テスト](#互換性テスト)
7. [トラブルシューティング](#トラブルシューティング)
8. [更新履歴](#更新履歴)

## 概要

本システムは、LinuxとmacOSの複数のOS環境で動作することを前提として設計されています。OS種類を自動判別し、各OSに最適なコマンドを選択することで、プラットフォーム間の互換性を確保しています。

**注意**: Windows環境ではWSL（Windows Subsystem for Linux）を使用してください。

### 主な特徴
- **自動OS判別**: `uname -s`を使用したOS種類の自動検出
- **コマンド切り替え**: OS別の最適なコマンドを動的に選択
- **共通インターフェース**: 統一された関数で環境変数やファイル操作を実行
- **テスト機能**: OS互換性を簡単に確認できるテストスクリプト

## 対応OS

### Linux
- **Ubuntu**: 20.04以降
- **CentOS**: 7以降
- **Debian**: 10以降
- **その他**: 主要なLinuxディストリビューション

### macOS
- **macOS**: 10.15 (Catalina)以降
- **Apple Silicon**: M1/M2 Mac対応
- **Intel Mac**: 従来のIntel Mac対応



## 自動判別機能

### OS判別ロジック
```bash
detect_os() {
    case "$(uname -s)" in
        Darwin*)    echo "macos" ;;
        Linux*)     echo "linux" ;;
        *)          echo "unknown" ;;
    esac
}
```

### 判別結果
- `Darwin*` → `macos`
- `Linux*` → `linux`
- その他 → `unknown`

## OS別コマンド設定

### macOS用コマンド
```bash
LS_VERSION_CMD="ls -1"  # -v オプションが利用できないため
SORT_CMD="sort -V"      # バージョン番号でソート
GREP_CMD="grep"         # 標準のgrep
CUT_CMD="cut"           # 標準のcut
```

### Linux用コマンド
```bash
LS_VERSION_CMD="ls -v"  # バージョン番号でソート済み
SORT_CMD="sort -V"      # バージョン番号でソート
GREP_CMD="grep"         # 標準のgrep
CUT_CMD="cut"           # 標準のcut
```



### 主な違い
- **バージョンディレクトリ取得**:
  - macOS: `ls -1 | sort -V`（2段階処理）
  - Linux: `ls -v`（1段階処理）

## 共通ユーティリティ

### 環境変数取得関数
```bash
get_env_value() {
    local key="$1"
    local env_file="$2"
    
    if [ -z "$env_file" ]; then
        env_file=".env"
    fi
    
    local value=$($GREP_CMD "^${key}=" "$env_file" | $CUT_CMD -d '=' -f2-)
    echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//'
}
```

### バージョンディレクトリ取得関数
```bash
get_version_dirs() {
    local base_dir="$1"
    local pattern="$2"
    
    if [ -z "$base_dir" ]; then
        base_dir="version"
    fi
    
    if [ -z "$pattern" ]; then
        pattern="v*"
    fi
    
    local os_type=$(detect_os)
    
    if [ "$os_type" = "macos" ]; then
        $LS_VERSION_CMD "${base_dir}/${pattern}" 2>/dev/null | $SORT_CMD
    else
        $LS_VERSION_CMD "${base_dir}/${pattern}" 2>/dev/null
    fi
}
```

## 互換性テスト

### テストコマンド
```bash
./syllabus.sh test-os
```

### テスト項目
1. **OS種類の判別**
   - 現在のOS環境の検出
   - 判別結果の表示

2. **OS別コマンド設定**
   - 各コマンドの設定値確認
   - 環境変数の設定状況

3. **バージョンディレクトリ取得テスト**
   - ディレクトリ存在確認
   - 取得結果の表示

4. **環境変数取得テスト**
   - .envファイルの存在確認
   - 環境変数の読み込みテスト

5. **コマンドの互換性テスト**
   - `ls -v`コマンドの利用可能性
   - `sort -V`コマンドの利用可能性
   - `grep`コマンドの利用可能性
   - `cut`コマンドの利用可能性

### テスト出力例
```
=== OS互換性テスト ===

1. OS種類の判別
検出されたOS: linux

2. OS別コマンド設定
LS_VERSION_CMD: ls -v
SORT_CMD: sort -V
GREP_CMD: grep
CUT_CMD: cut

3. バージョンディレクトリ取得テスト
バージョンディレクトリが存在しません

4. 環境変数取得テスト
.envファイルが存在します
POSTGRES_DB: syllabus_db

5. コマンドの互換性テスト
ls -v コマンドのテスト:
  ✓ ls -v が利用可能です
sort -V コマンドのテスト:
  ✓ sort -V が利用可能です
grep コマンドのテスト:
  ✓ grep が利用可能です
cut コマンドのテスト:
  ✓ cut が利用可能です

=== テスト完了 ===
```

## トラブルシューティング

### よくある問題

#### 0. 実行権限が失われている（macOS）
**症状**: `Permission denied`エラーが発生
**原因**: macOSでレポジトリをクローンした際に実行権限が失われる
**解決策**: 
```bash
# 手動で権限を復元
chmod +x bin/*.sh
chmod +x syllabus.sh

# または専用スクリプトを使用
./bin/restore-permissions.sh
```

#### 1. `ls -v`コマンドが利用できない
**症状**: macOSでバージョンディレクトリの取得に失敗
**原因**: macOSでは`ls -v`オプションが利用できない
**解決策**: 自動的に`ls -1 | sort -V`に切り替わります

#### 2. 環境変数の読み込みエラー
**症状**: `.env`ファイルから値が正しく読み込まれない
**原因**: OS別の`grep`や`cut`コマンドの違い
**解決策**: 共通関数`get_env_value()`を使用してください

#### 3. バージョンディレクトリの順序が正しくない
**症状**: バージョン番号の順序が期待と異なる
**原因**: OS別のソート方法の違い
**解決策**: 自動的に適切なソート方法が選択されます

### デバッグ方法

#### 1. OS判別の確認
```bash
./syllabus.sh test-os | grep "検出されたOS"
```

#### 2. コマンド設定の確認
```bash
./syllabus.sh test-os | grep -A 4 "OS別コマンド設定"
```

#### 3. 個別コマンドのテスト
```bash
# ls -v のテスト
ls -v /dev/null >/dev/null 2>&1 && echo "OK" || echo "NG"

# sort -V のテスト
echo "v1.0 v2.0 v1.1" | tr ' ' '\n' | sort -V >/dev/null 2>&1 && echo "OK" || echo "NG"
```

## 更新履歴

### v1.0.0 (2025-07-03)
- 初回作成
- OS自動判別機能の追加
- 共通ユーティリティ関数の実装
- 互換性テストスクリプトの追加

[�� ページトップへ](#os互換性) 