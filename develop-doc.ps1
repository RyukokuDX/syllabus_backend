# PowerShellスクリプトの実行ポリシーを確認
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    Write-Host "PowerShellの実行ポリシーが制限されています。"
    Write-Host "以下のコマンドで実行ポリシーを変更してください："
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
    exit 1
}

# エラーが発生したら即座に終了
$ErrorActionPreference = "Stop"

try {
    # Gitが利用可能か確認
    $gitVersion = git --version
    if (-not $?) {
        throw "Gitがインストールされていないか、PATHに設定されていません"
    }

    # リポジトリのルートディレクトリにいるか確認
    $isGitRepo = git rev-parse --is-inside-work-tree
    if (-not $?) {
        throw "Gitリポジトリのルートディレクトリで実行してください"
    }

    # developブランチの存在確認
    $developExists = git show-ref --verify --quiet refs/heads/develop
    if (-not $?) {
        throw "developブランチが存在しません"
    }

    # 現在のブランチ名を取得
    $currentBranch = git rev-parse --abbrev-ref HEAD
    Write-Host "現在のブランチ: $currentBranch"

    # 変更されたファイルを取得
    $changedFiles = git diff --name-only develop
    if (-not $?) {
        throw "developブランチとの差分の取得に失敗しました"
    }

    # データベースドキュメントの変更を抽出
    $databaseDocs = $changedFiles | Where-Object { $_ -match "^docs/database/.*\.md$" }

    if (-not $databaseDocs) {
        Write-Host "docs/database/*.mdファイルの変更が見つかりません"
        exit 0
    }

    # ファイルの存在確認
    $existingDocs = @()
    foreach ($file in $databaseDocs) {
        if (Test-Path $file) {
            $existingDocs += $file
        } else {
            Write-Host "警告: ファイルが存在しません: $file"
        }
    }

    if (-not $existingDocs) {
        Write-Host "マージ可能なファイルが見つかりません"
        exit 0
    }

    Write-Host "`nマージ対象のファイル:"
    $existingDocs | ForEach-Object { Write-Host "- $_" }

    # 確認プロンプト
    $confirmation = Read-Host "`nこれらのファイルをdevelopブランチにマージしますか？ (y/N)"
    if ($confirmation -ne "y") {
        Write-Host "マージを中止しました"
        exit 0
    }

    # developブランチに切り替え
    Write-Host "`ndevelopブランチに切り替え中..."
    git checkout develop
    if (-not $?) {
        throw "developブランチへの切り替えに失敗しました"
    }

    # 変更をマージ
    Write-Host "`nファイルをマージ中..."
    foreach ($file in $existingDocs) {
        git checkout $currentBranch -- $file
        if (-not $?) {
            throw "ファイルのマージに失敗しました: $file"
        }
        Write-Host "- $file をマージしました"
    }

    # 変更をコミット
    $commitMessage = "docs: データベース設計ドキュメントの更新"
    Write-Host "`n変更をコミット中..."
    git add $existingDocs
    if (-not $?) {
        throw "ファイルのステージングに失敗しました"
    }

    git commit -m $commitMessage
    if (-not $?) {
        throw "コミットに失敗しました"
    }

    Write-Host "`nマージが完了しました"
    Write-Host "元のブランチに戻りますか？ (y/N)"
    $returnToBranch = Read-Host
    if ($returnToBranch -eq "y") {
        git checkout $currentBranch
        if (-not $?) {
            throw "元のブランチへの切り替えに失敗しました"
        }
        Write-Host "元のブランチ ($currentBranch) に戻りました"
    }

} catch {
    Write-Host "`nエラーが発生しました:"
    Write-Host $_.Exception.Message
    Write-Host "`nスタックトレース:"
    Write-Host $_.ScriptStackTrace
    exit 1
} 