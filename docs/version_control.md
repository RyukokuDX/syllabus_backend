<!--
更新時の注意事項:
- 準拠とは、類推せずに内容に従うこと
- file作成や削除は、必ず事前に承認を受けること
- 更新は docs/doc.md に準拠すること
- 更新の登録を要求された場合は、/docs/version_control.md に準拠して実行
-->

# check-with-dev-db.sh (v1.0.1)

[readmeへ](../README.md) | [ドキュメント作成ガイドラインへ](../doc.md) | [syllabus.shへ](./syllabus.md)

## Version 管理概要
### update
1. ファイルの更新発生
2. 差分sqlfile生成(更新サマリーを登録)
3. 更新作成

## バージョン管理構造
```
project/
├── docs/
│   └── database/
│       └── structure.md
└── version/
    └── v1.0/
        └── docs/
            └── database/
                └── structure.md.json
```

### バージョン管理ファイル形式
```json
{
  "meta_data": {
    "version": "1.0.2",
    "created_at": "2024-03-20T10:00:00Z"
  },
  "path_level": {
    "1": {
      "summary": "テーブル定義の追加",
      "date": "2024-03-20-10-00",
      "details": "subjectテーブルの定義を追加"
    },
    "2": {
      "summary": "カラムの追加",
      "date": "2024-03-21-15-30",
      "details": "subjectテーブルにcodeカラムを追加"
    }
  }
}
```

### version番号
{major_version}.{minor_version}.{patch_version}の形をとる
- major_version: 後方互換性のない変更
- minor_version: 後方互換性のある機能追加
- patch_version: バグ修正や軽微な変更（JSONファイル内で管理）

## Cursor用の指示
### JSONファイルの作成
1. 新しいバージョンディレクトリの作成
```bash
mkdir -p version/v{major}.{minor}/docs/database
```

2. JSONファイルの作成
```bash
# テンプレートの作成
cat > version/v{major}.{minor}/docs/database/structure.md.json << EOF
{
  "meta_data": {
    "version": "{major}.{minor}.{patch}",
    "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  },
  "path_level": {
    "1": {
      "summary": "変更の概要",
      "date": "$(date +"%Y-%m-%d-%H-%M")",
      "details": "変更の詳細"
    }
  }
}
EOF
```

### JSONファイルの更新
1. 既存のJSONファイルを読み込む
```bash
# 最新のバージョンを取得
latest_version=$(ls -v version/v* | tail -n 1)
json_file="${latest_version}/docs/database/structure.md.json"
```

2. 新しい変更を追加
```bash
# 現在のpath_levelの最大値を取得
max_level=$(jq '.path_level | keys | map(tonumber) | max' "$json_file")

# 新しい変更を追加
jq --arg level $((max_level + 1)) \
   --arg date "$(date +"%Y-%m-%d-%H-%M")" \
   --arg summary "新しい変更の概要" \
   --arg details "新しい変更の詳細" \
   '.path_level[$level] = {"summary": $summary, "date": $date, "details": $details}' \
   "$json_file" > "${json_file}.tmp" && mv "${json_file}.tmp" "$json_file"
```

### fileの更新
- Json更新後、更新対処の文頭付近のversion番号を更新

[🔝 ページトップへ](#check-with-dev-dbsh) 