import os
from dotenv import load_dotenv
from src.db.parser.17_subject import main as subject_main

def main():
    # .envファイルを読み込む
    load_dotenv()
    
    # データベース設定を取得
    db_config = {
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT'),
        'db': os.getenv('POSTGRES_DB')
    }
    
    # 17_subject.pyを実行
    subject_main(db_config)

if __name__ == "__main__":
    main() 