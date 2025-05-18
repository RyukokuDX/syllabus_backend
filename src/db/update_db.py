import json
from pathlib import Path
from typing import Dict, Any, List, Type, TypeVar
from datetime import datetime
import shutil
import logging
from src.db.database import Database
from dataclasses import asdict
from src.db.models import (
    Subject, Syllabus, SyllabusTime, Instructor, Book, GradingCriterion,
    SyllabusInstructor, LectureSession, SyllabusTextbook, SyllabusReference,
    SyllabusFaculty, SubjectRequirement, SubjectProgram
)

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db/updates/update.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

T = TypeVar('T')

def load_and_validate_json(file_path: Path, model_class: Type[T]) -> List[T]:
    """JSONファイルを読み込み、データクラスのインスタンスとして検証"""
    logger.info(f"JSONファイルを読み込み中: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not isinstance(data, dict):
        raise ValueError(f"{file_path}: JSONファイルはオブジェクトである必要があります")
    
    content = data.get('content', [])
    if not isinstance(content, list):
        content = [content]
    
    # データクラスのインスタンス化を試みる（これにより型チェックが行われる）
    instances = []
    for i, item in enumerate(content):
        try:
            instance = model_class(**item)
            instances.append(instance)
            logger.debug(f"レコード {i + 1} を正常に検証: {item}")
        except TypeError as e:
            logger.error(f"レコード {i + 1} の型エラー: {str(e)}")
            raise ValueError(f"{file_path} の項目 {i + 1}: {str(e)}")
        except ValueError as e:
            logger.error(f"レコード {i + 1} の値エラー: {str(e)}")
            raise ValueError(f"{file_path} の項目 {i + 1}: {str(e)}")
    
    logger.info(f"{len(instances)}件のレコードを検証完了")
    return instances

def insert_records(cur, instances: List[T], table_name: str, operation: str):
    """データベースにレコードを挿入または更新"""
    if not instances:
        logger.warning("処理対象のレコードがありません")
        return
    
    # インスタンスを辞書に変換
    records = [asdict(instance) for instance in instances]
    
    # カラム名を取得
    columns = list(records[0].keys())
    placeholders = ','.join(['?' for _ in columns])
    columns_str = ','.join(columns)
    
    # SQLクエリの構築
    if operation == 'add':
        query = f"""
        INSERT OR REPLACE INTO {table_name} ({columns_str})
        VALUES ({placeholders})
        """
        logger.info(f"INSERTクエリを実行: {table_name}")
    else:  # modify
        # 主キーを特定（subject_codeまたはsyllabus_id）
        primary_key = 'subject_code' if 'subject_code' in columns else 'syllabus_id'
        set_clause = ', '.join([f"{col} = ?" for col in columns if col != primary_key])
        query = f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE {primary_key} = ?
        """
        logger.info(f"UPDATEクエリを実行: {table_name}")
    
    # レコードの挿入または更新
    for i, record in enumerate(records):
        try:
            if operation == 'add':
                values = [record[column] for column in columns]
            else:  # modify
                # 主キー以外のカラムの値を取得
                values = [record[column] for column in columns if column != primary_key]
                # 主キーの値を最後に追加
                values.append(record[primary_key])
            
            cur.execute(query, values)
            logger.debug(f"レコード {i + 1} を処理: {record}")
        except Exception as e:
            logger.error(f"レコード {i + 1} の処理中にエラー: {str(e)}")
            raise

def move_to_registered(json_file: Path):
    """処理済みのJSONファイルをregisteredディレクトリに移動"""
    # 移動先のディレクトリパスを構築
    # db/updates/[データ型]/registered/YYYY-MM/[ファイル名]
    data_type = json_file.parent.parent.name
    current_date = datetime.now().strftime('%Y-%m')
    registered_dir = json_file.parent.parent / "registered" / current_date
    registered_dir.mkdir(parents=True, exist_ok=True)

    # 移動先のファイル名を生成（同名ファイルが存在する場合は連番を付加）
    target_path = registered_dir / json_file.name
    counter = 1
    while target_path.exists():
        stem = json_file.stem
        suffix = json_file.suffix
        target_path = registered_dir / f"{stem}_{counter}{suffix}"
        counter += 1

    # ファイルを移動
    shutil.move(str(json_file), str(target_path))
    logger.info(f"ファイルを移動: {json_file} -> {target_path}")

def main():
    """メイン処理"""
    logger.info("データベース更新処理を開始")
    
    # モデルクラスとテーブル名のマッピング
    model_mapping = {
        'subject': (Subject, 'subject'),
        'syllabus': (Syllabus, 'syllabus'),
        'syllabus_time': (SyllabusTime, 'syllabus_time'),
        'instructor': (Instructor, 'instructor'),
        'book': (Book, 'book'),
        'grading_criterion': (GradingCriterion, 'grading_criterion'),
        'syllabus_instructor': (SyllabusInstructor, 'syllabus_instructor'),
        'lecture_session': (LectureSession, 'lecture_session'),
        'syllabus_textbook': (SyllabusTextbook, 'syllabus_textbook'),
        'syllabus_reference': (SyllabusReference, 'syllabus_reference'),
        'syllabus_faculty': (SyllabusFaculty, 'syllabus_faculty'),
        'subject_requirement': (SubjectRequirement, 'subject_requirement'),
        'subject_program': (SubjectProgram, 'subject_program')
    }

    db = Database.get_instance()
    updates_dir = Path("db/updates")
    
    try:
        # 1. JSONファイルの検索（addとmodifyディレクトリのみ）
        json_files = []
        for operation in ['add', 'modify']:
            files = list(updates_dir.glob(f"*/{operation}/*.json"))
            json_files.extend(files)
            logger.info(f"{operation}ディレクトリから{len(files)}件のファイルを検出")
        
        if not json_files:
            logger.warning("更新対象のJSONファイルが見つかりませんでした。")
            return
        
        # 2. 各JSONファイルの処理
        for json_file in json_files:
            logger.info(f"\n{json_file}を処理中...")
            
            # ファイル名からデータ型を判断
            data_type = json_file.parent.parent.name
            if data_type not in model_mapping:
                logger.error(f"未知のデータ型です: {data_type}")
                print("処理を中止します。")
                exit(1)
            
            model_class, table_name = model_mapping[data_type]
            operation = json_file.parent.name  # 'add' または 'modify'
            
            try:
                # データの整合性チェック
                instances = load_and_validate_json(json_file, model_class)
                
                # データベースの更新
                with db.get_cursor() as cur:
                    insert_records(cur, instances, table_name, operation)
                
                logger.info(f"✓ {len(instances)}件のレコードを正常に処理しました。")
                
                # 処理済みファイルの移動
                move_to_registered(json_file)
                
            except ValueError as e:
                logger.error(f"データの整合性チェックに失敗しました: {str(e)}")
                print("処理を中止します。")
                exit(1)
            except Exception as e:
                logger.error(f"データベースの更新中にエラーが発生しました: {str(e)}")
                print("処理を中止します。")
                exit(1)
        
        logger.info("\nすべてのファイルが正常に処理されました。")
        
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {str(e)}")
        print("処理を中止します。")
        exit(1)

if __name__ == "__main__":
    main() 