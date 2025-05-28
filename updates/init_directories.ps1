# 必要なディレクトリを作成するスクリプト

# スクリプトの実行ディレクトリを取得
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 作成するディレクトリのリスト
$directories = @(
    "class/add",
    "subclass/add",
    "class_note/add",
    "subject_name/add",
    "subject/add",
    "faculty/add",
    "instructor/add",
    "criteria/add",
    "book/add",
    "syllabus/add",
    "syllabus_faculty_enrollment/add",
    "lecture_session/add",
    "syllabus_instructor/add",
    "syllabus_book/add",
    "grading_criterion/add"
)

# 各ディレクトリを作成
foreach ($dir in $directories) {
    $path = Join-Path $scriptPath $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force
        Write-Host "Created directory: $path"
    } else {
        Write-Host "Directory already exists: $path"
    }
}

Write-Host "`nAll directories have been created." 