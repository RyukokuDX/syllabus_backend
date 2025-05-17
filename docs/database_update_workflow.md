# シラバスデータベース開発フローの考察

[readmeへ](../README.md) | [DB構造へ](database_structure.md)

## DB更新手順

1. JSONファイルの作成(簡易)
   - 追加の場合
      `db/updates/{table名}/add/`にjsonを追加
   - 変更の場合
      `db/updates/{table名}/modify/`にjsonを追加

2. Cursorへの依頼
   ``` Cursor
   @Cursor JSONファイルの適用をお願いします
   ```

## Cusorの処理
   - JSONファイルの検証
   - SQLiteデータベースへの適用
   - 結果のログ記録

## バックアップと運用管理

1. **定期バックアップ**
   ```bash
   # バックアップスクリプト
   sqlite3 db/syllabus.db ".backup 'db/backups/syllabus_$(date +%Y%m%d).db'"
   ```

2. **整合性チェック**
   ```bash
   # データベースの整合性確認
   sqlite3 db/syllabus.db "PRAGMA integrity_check"
   ```
[🔝 ページトップへ](#)