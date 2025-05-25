#!/usr/bin/env pwsh

# エラーが発生したら即座に終了
$ErrorActionPreference = "Stop"

# 現在のブランチ名を取得
$currentBranch = git rev-parse --abbrev-ref HEAD
Write-Host "現在のブランチ: $currentBranch"

# 変更されたファイルを取得
$changedFiles = git diff --name-only develop
$databaseDocs = $changedFiles | Where-Object { $_ -match "^docs/database/.*\.md$" }

if (-not $databaseDocs) {
    Write-Host "docs/database/*.mdファイルの変更が見つかりません"
    exit 0
}

Write-Host "`nマージ対象のファイル:"
$databaseDocs | ForEach-Object { Write-Host "- $_" }

# 確認プロンプト
$confirmation = Read-Host "`nこれらのファイルをdevelopブランチにマージしますか？ (y/N)"
if ($confirmation -ne "y") {
    Write-Host "マージを中止しました"
    exit 0
}

# developブランチに切り替え
Write-Host "`ndevelopブランチに切り替え中..."
git checkout develop

# 変更をマージ
Write-Host "`nファイルをマージ中..."
foreach ($file in $databaseDocs) {
    git checkout $currentBranch -- $file
    Write-Host "- $file をマージしました"
}

# 変更をコミット
$commitMessage = "docs: データベース設計ドキュメントの更新"
Write-Host "`n変更をコミット中..."
git add $databaseDocs
git commit -m $commitMessage

Write-Host "`nマージが完了しました"
Write-Host "元のブランチに戻りますか？ (y/N)"
$returnToBranch = Read-Host
if ($returnToBranch -eq "y") {
    git checkout $currentBranch
    Write-Host "元のブランチ ($currentBranch) に戻りました"
} 