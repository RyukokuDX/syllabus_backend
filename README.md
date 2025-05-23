# シラバスバックエンド

## 概要
シラバス情報を管理するバックエンドシステム

## ディレクトリ構造
```
.
├── .github/                  # GitHub設定
├── .gitignore               # Git除外設定
├── .dockerignore           # Docker除外設定
├── docs/                    # ドキュメント
│   ├── database/           # データベース関連
│   ├── python/             # Python関連
│   ├── docker/             # Docker関連
│   ├── githelp.md          # Git操作ガイド
│   ├── cursor.md           # Cursorへの指示
│   └── doc.md              # ドキュメント
├── docker/                  # Docker関連
│   ├── postgresql/         # PostgreSQL設定
│   │   ├── init/          # 初期化スクリプト
│   │   ├── Dockerfile     # PostgreSQL用Dockerfile
│   │   ├── postgresql.conf # PostgreSQL設定ファイル
│   │   ├── docker-compose.yml # PostgreSQL用docker-compose
│   │   ├── generate-init.sh   # 初期化スクリプト生成
│   │   ├── start-postgres.ps1 # 起動スクリプト
│   │   ├── stop-postgres.ps1  # 停止スクリプト
│   │   ├── check-postgres.ps1 # 状態確認スクリプト
│   │   └── check-with-dev-db.ps1 # 開発DB確認スクリプト
│   └── fastapi/            # FastAPI設定
│       ├── app/            # アプリケーションコード
│       ├── Dockerfile      # FastAPI用Dockerfile
│       ├── docker-compose.yml # FastAPI用docker-compose
│       └── pyproject.toml  # Pythonプロジェクト設定
├── src/                     # ソースコード
│   ├── db/                 # データベース関連
│   ├── course_guide/       # 要項関連
│   ├── syllabus/           # シラバス関連
│   └── __init__.py         # パッケージ定義
├── updates/                 # 更新用ファイル
└── README.md               # 本ドキュメント
```

## 開発環境
- Python 3.11
- SQLite 3
- FastAPI

## セットアップ
1. リポジトリのクローン
```bash
git clone https://github.com/your-username/syllabus_backend.git
cd syllabus_backend
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

4. データベースの初期化
```bash
python src/db/init_db.py
```

## 開発ガイドライン
- [データベース設計ポリシー](docs/database/policy.md)
- [API仕様](docs/api/openapi.yaml)
- [データベース構造定義](docs/database/structure.md)
- [Git操作ガイド](docs/githelp.md)
- [Cursorへの指示](docs/cursor.md)

## ライセンス
MIT License
