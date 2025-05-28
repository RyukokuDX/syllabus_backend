# updates/*/add/ディレクトリ内のファイルを削除するスクリプト

# スクリプトの実行ディレクトリを取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# updatesディレクトリ内のすべてのサブディレクトリを取得
$addDirs = Get-ChildItem -Path $scriptPath -Directory | 
    Where-Object { $_.Name -ne "init_updates.ps1" } | 
    ForEach-Object { Join-Path $_.FullName "add" }

# 各addディレクトリ内のファイルを削除
foreach ($dir in $addDirs) {
    if (Test-Path $dir) {
        Write-Host "Cleaning directory: $dir"
        Get-ChildItem -Path $dir -File | Remove-Item -Force
        Write-Host "All files in $dir have been removed."
    }
}

Write-Host "`nAll update directories have been cleaned." 