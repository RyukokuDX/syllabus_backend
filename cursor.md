+ 指示していない新規ファイルの生成/削除は禁止
+ 指示していない箇所の類推による変更は承認を必ず得る
+ 準拠と指示した場合は、類推を禁止。準拠元を厳密に反映
+ ps1ファイルにはutf8withbom, shではutf8(bom無)
+ 更新は既存のファイルの更新であり、新規ファイルの生成要求ではない
+ docs/database/structure.mdの更新の際は
    - docs/database/policy.mdに準拠
    - 承認後, docs/database/structure.mdに準拠して、以下を更新
        - docs/database/er.md
        - src/db/models.py
        - docker/postgresql/init/init.sql.template
        - src/db/migratinos/*.py