from typing import Dict, List, Tuple
import os
import json
import sys
import csv
import logging
from datetime import datetime

def setup_logger(year: int) -> logging.Logger:
    """ロガーの設定"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = f"{log_dir}/01_syllabus_list_master_{timestamp}.log"

    logger = logging.getLogger(f"01_syllabus_list_master_{year}")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def parse_csv_file(file_path: str, logger: logging.Logger) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict], List[Dict]]:
    """CSVファイルを解析して各マスターデータを抽出
    Args:
        file_path (str): CSVファイルのパス
        logger (logging.Logger): ロガー
    Returns:
        Tuple[List[Dict], List[Dict], List[Dict], List[Dict], List[Dict]]: 
            科目区分、科目小区分、科目区分の備考、科目名、学部のリスト
    """
    class_entries = []
    subclass_entries = []
    class_note_entries = []
    subject_name_entries = []
    faculty_entries = []

    seen_classes = set()
    seen_subclasses = set()
    seen_class_notes = set()
    seen_subject_names = set()
    seen_faculties = set()

    def is_subclass_name(name: str) -> bool:
        """科目小区分かどうかを判定"""
        return any(name.endswith(suffix) for suffix in ["系", "コース", "分野", "専攻"])

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 属性の処理
            attribute = row.get("属性", "").strip()
            if attribute:
                # 「：」がある場合は左をclass_note
                if "：" in attribute:
                    class_note = attribute.split("：")[0].strip()
                    attribute = attribute.split("：")[1].strip()
                    if class_note and class_note not in seen_class_notes:
                        # 学年指定が含まれている場合はclass_noteとして登録しない
                        if "年度入学生" not in class_note:
                            class_note_entries.append({"class_note": class_note})
                            seen_class_notes.add(class_note)
                            logger.info(f"科目区分の備考を追加: {class_note}")

                # 「・」がある場合は右をsubclass、左をclass
                if "・" in attribute:
                    parts = attribute.split("・")
                    left = parts[0].strip()
                    right = parts[1].strip()
                    
                    if left and left not in seen_classes:
                        class_entries.append({"class_name": left})
                        seen_classes.add(left)
                        logger.info(f"科目区分を追加: {left}")
                    
                    if right and right not in seen_subclasses:
                        subclass_entries.append({"subclass_name": right})
                        seen_subclasses.add(right)
                        logger.info(f"科目小区分を追加: {right}")
                # その他の場合は「系」で終わる場合をsubclass、それ以外はclass
                else:
                    if attribute.endswith("系"):
                        if attribute not in seen_subclasses:
                            subclass_entries.append({"subclass_name": attribute})
                            seen_subclasses.add(attribute)
                            logger.info(f"科目小区分を追加: {attribute}")
                    else:
                        if attribute not in seen_classes:
                            class_entries.append({"class_name": attribute})
                            seen_classes.add(attribute)
                            logger.info(f"科目区分を追加: {attribute}")

            # 科目名の処理
            subject_name = row.get("科目名", "").strip()
            if subject_name and subject_name not in seen_subject_names:
                subject_name_entries.append({"name": subject_name})
                seen_subject_names.add(subject_name)
                logger.info(f"科目名を追加: {subject_name}")

            # 学部の処理
            faculty = row.get("学部", "").strip()
            if faculty and faculty not in seen_faculties:
                faculty_entries.append({"faculty_name": faculty})
                seen_faculties.add(faculty)
                logger.info(f"学部を追加: {faculty}")

    return class_entries, subclass_entries, class_note_entries, subject_name_entries, faculty_entries

def save_json(data: List[Dict], data_type: str, year: int, logger: logging.Logger) -> None:
    """データをJSONファイルとして保存"""
    output_dir = f"updates/{data_type}/add"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/{data_type}_{year}.json"

    # 配列名のマッピング
    array_names = {
        'class': 'classes',
        'subclass': 'subclasses',
        'class_note': 'class_notes',
        'subject_name': 'subject_names',
        'faculty': 'faculties'
    }

    # データを配列名でラップ
    json_data = {array_names.get(data_type, f"{data_type}s"): data}

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    logger.info(f"{data_type}のデータを保存: {output_file}")

def process_syllabus_list_master_data(year: int) -> None:
    """シラバス一覧データからマスターデータを処理
    Args:
        year (int): 処理対象の年度
    """
    logger = setup_logger(year)
    logger.info(f"{year}年度のシラバス一覧データからマスターデータの処理を開始")

    input_file = f"src/syllabus/{year}/search_page/syllabus_list.csv"
    if not os.path.exists(input_file):
        logger.error(f"入力ファイルが見つかりません: {input_file}")
        return

    try:
        class_entries, subclass_entries, class_note_entries, subject_name_entries, faculty_entries = parse_csv_file(input_file, logger)

        # 各データをJSONファイルとして保存
        save_json(class_entries, "class", year, logger)
        save_json(subclass_entries, "subclass", year, logger)
        save_json(class_note_entries, "class_note", year, logger)
        save_json(subject_name_entries, "subject_name", year, logger)
        save_json(faculty_entries, "faculty", year, logger)

        # 処理結果のサマリーを標準出力に表示
        print("\n処理結果サマリー:")
        print(f"科目区分: {len(class_entries)}件 -> updates/class/add/class_{year}.json")
        print(f"科目小区分: {len(subclass_entries)}件 -> updates/subclass/add/subclass_{year}.json")
        print(f"科目区分の備考: {len(class_note_entries)}件 -> updates/class_note/add/class_note_{year}.json")
        print(f"科目名: {len(subject_name_entries)}件 -> updates/subject_name/add/subject_name_{year}.json")
        print(f"学部: {len(faculty_entries)}件 -> updates/faculty/add/faculty_{year}.json")
        print("処理が正常に完了しました")

        # 処理結果のログを出力
        logger.info("処理結果:")
        logger.info(f"科目区分: {len(class_entries)}件 -> updates/class/add/class_{year}.json")
        logger.info(f"科目小区分: {len(subclass_entries)}件 -> updates/subclass/add/subclass_{year}.json")
        logger.info(f"科目区分の備考: {len(class_note_entries)}件 -> updates/class_note/add/class_note_{year}.json")
        logger.info(f"科目名: {len(subject_name_entries)}件 -> updates/subject_name/add/subject_name_{year}.json")
        logger.info(f"学部: {len(faculty_entries)}件 -> updates/faculty/add/faculty_{year}.json")
        logger.info("処理が正常に完了しました")

    except Exception as e:
        logger.error(f"処理中にエラーが発生: {str(e)}")
        raise

if __name__ == "__main__":
    # 年指定がない場合は入力を促す
    if len(sys.argv) == 1:
        year_input = input("年度を入力してください（空の場合は今年）: ").strip()
        if year_input:
            year = int(year_input)
        else:
            year = datetime.now().year
    elif len(sys.argv) == 2:
        year = int(sys.argv[1])
    else:
        print("使用方法: python 01_syllabus_list_master.py [年度]")
        sys.exit(1)
    
    process_syllabus_list_master_data(year) 