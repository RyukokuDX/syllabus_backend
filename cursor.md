+ 指示していない新規ファイルの生成/削除は禁止
+ 指示していない箇所の類推による変更は承認を必ず得る
+ ps1ファイルにはutf8withbom, shではutf8(bom無)
+ 更新は既存のファイルの更新であり、新規ファイルの生成要求ではない
+ docs/database/structure.mdの更新の際は
    - docs/database/policy.mdで生成規則を確認
    - 承認後の更新ファイルは
        - docs/database/er.md
        - src/db/models.py
        - docker/postgresql/init/init.sql.template
        - src/db/migratinos/*.py