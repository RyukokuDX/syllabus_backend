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
    log_file = f"{log_dir}/syllabus_list_{timestamp}.log"

    logger = logging.getLogger(f"syllabus_list_{year}")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

def convert_fullwidth_to_halfwidth(text: str) -> str:
    """全角数字を半角数字に変換"""
    fullwidth_digits = "０１２３４５６７８９"
    halfwidth_digits = "0123456789"
    for f, h in zip(fullwidth_digits, halfwidth_digits):
        text = text.replace(f, h)
    return text

def parse_enrollment_years(note: str) -> List[int]:
    """入学年度制限の文字列を解析して年度のリストを返す"""
    years = []
    if not note or "年度入学生" not in note:
        return years

    # 全角数字を半角数字に変換
    note = convert_fullwidth_to_halfwidth(note)
    
    # カンマで分割して複数の指定を処理
    for part in note.split("、"):
        part = part.strip()
        if "～" in part:
            # 年度範囲の処理
            try:
                start_year = int(part.split("～")[0].replace("年度入学生", "").replace("年度", "").strip())
                end_year = int(part.split("～")[1].replace("年度入学生", "").replace("年度", "").strip())
                years.extend(range(start_year, end_year + 1))
            except ValueError:
                continue
        else:
            # 単一年度の処理
            try:
                year = int(part.replace("年度入学生", "").replace("年度", "").strip())
                years.append(year)
            except ValueError:
                continue
    
    return years

def parse_csv_file(file_path: str, logger: logging.Logger, year: int) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict], List[Dict], List[Dict], List[Dict]]:
    """CSVファイルを解析して各データを抽出
    Args:
        file_path (str): CSVファイルのパス
        logger (logging.Logger): ロガー
        year (int): 処理対象の年度
    Returns:
        Tuple[List[Dict], List[Dict], List[Dict], List[Dict], List[Dict], List[Dict], List[Dict]]: 
            科目区分、科目小区分、科目区分の備考、科目名、履修可能学年、入学年度制限、学部のリスト
    """
    class_entries = []
    subclass_entries = []
    class_note_entries = []
    subject_name_entries = []
    syllabus_eligible_grade_entries = []
    syllabus_enrollment_year_entries = []
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
                        # 学年指定が含まれている場合はclass_noteとして登録せず、syllabus_enrollment_yearに追加
                        if "年度入学生" in class_note:
                            # 全角数字を半角数字に変換
                            class_note = convert_fullwidth_to_halfwidth(class_note)
                            # 年度範囲の処理（例：２０１５～２０１９年度入学生）
                            if "～" in class_note:
                                start_year = int(class_note.split("～")[0].replace("年度入学生", "").replace("年度", "").strip())
                                end_year = int(class_note.split("～")[1].replace("年度入学生", "").replace("年度", "").strip())
                                for year in range(start_year, end_year + 1):
                                    syllabus_enrollment_year_entries.append({
                                        "syllabus_code": row["シラバス管理番号"],
                                        "enrollment_year": year
                                    })
                                    logger.info(f"入学年度制限を追加: {year}年度")
                            # 単一年度の処理（例：２０１５年度入学生）
                            else:
                                year = int(class_note.replace("年度入学生", "").replace("年度", "").strip())
                                syllabus_enrollment_year_entries.append({
                                    "syllabus_code": row["シラバス管理番号"],
                                    "enrollment_year": year
                                })
                                logger.info(f"入学年度制限を追加: {year}年度")
                        else:
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

            # 履修可能学年の処理
            grade = row.get("配当年次", "").strip()
            if grade:
                # 全角数字を半角数字に変換
                grade = convert_fullwidth_to_halfwidth(grade)
                # 学年範囲の処理（例：「1年次～4年次」）
                if "～" in grade:
                    start_grade = grade.split("～")[0].replace("年次", "").strip()
                    end_grade = grade.split("～")[1].replace("年次", "").strip()
                    for g in range(int(start_grade), int(end_grade) + 1):
                        syllabus_eligible_grade_entries.append({
                            "syllabus_code": row["シラバス管理番号"],
                            "syllabus_year": year,
                            "grade": f"学部{g}年"
                        })
                        logger.info(f"履修可能学年を追加: 学部{g}年")
                # 単一年度の処理（例：「1年次」）
                else:
                    grade = grade.replace("年次", "").strip()
                    syllabus_eligible_grade_entries.append({
                        "syllabus_code": row["シラバス管理番号"],
                        "syllabus_year": year,
                        "grade": f"学部{grade}年"
                    })
                    logger.info(f"履修可能学年を追加: 学部{grade}年")

            # 学部の処理
            faculty = row.get("学部", "").strip()
            if faculty and faculty not in seen_faculties:
                faculty_entries.append({"faculty_name": faculty})
                seen_faculties.add(faculty)
                logger.info(f"学部を追加: {faculty}")

    return class_entries, subclass_entries, class_note_entries, subject_name_entries, syllabus_eligible_grade_entries, syllabus_enrollment_year_entries, faculty_entries

def save_json(data: List[Dict], data_type: str, year: int, logger: logging.Logger) -> None:
    """データをJSONファイルとして保存"""
    output_dir = f"updates/{data_type}/add"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/{data_type}_{year}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"{data_type}のデータを保存: {output_file}")

def process_syllabus_list_data(year: int) -> None:
    """シラバス一覧データを処理
    Args:
        year (int): 処理対象の年度
    """
    logger = setup_logger(year)
    logger.info(f"{year}年度のシラバス一覧データの処理を開始")

    input_file = f"src/syllabus/{year}/search_page/syllabus_list.csv"
    if not os.path.exists(input_file):
        logger.error(f"入力ファイルが見つかりません: {input_file}")
        return

    try:
        class_entries, subclass_entries, class_note_entries, subject_name_entries, syllabus_eligible_grade_entries, syllabus_enrollment_year_entries, faculty_entries = parse_csv_file(input_file, logger, year)

        # 各データをJSONファイルとして保存
        save_json(class_entries, "class", year, logger)
        save_json(subclass_entries, "subclass", year, logger)
        save_json(class_note_entries, "class_note", year, logger)
        save_json(subject_name_entries, "subject_name", year, logger)
        save_json(syllabus_eligible_grade_entries, "syllabus_eligible_grade", year, logger)
        save_json(syllabus_enrollment_year_entries, "syllabus_enrollment_year", year, logger)
        save_json(faculty_entries, "faculty", year, logger)

        # 処理結果のサマリーを標準出力に表示
        print("\n処理結果サマリー:")
        print(f"科目区分: {len(class_entries)}件")
        print(f"科目小区分: {len(subclass_entries)}件")
        print(f"科目区分の備考: {len(class_note_entries)}件")
        print(f"科目名: {len(subject_name_entries)}件")
        print(f"履修可能学年: {len(syllabus_eligible_grade_entries)}件")
        print(f"入学年度制限: {len(syllabus_enrollment_year_entries)}件")
        print(f"学部: {len(faculty_entries)}件")
        print("処理が正常に完了しました")

        # 処理結果のログを出力
        logger.info("処理結果:")
        logger.info(f"科目区分: {len(class_entries)}件")
        logger.info(f"科目小区分: {len(subclass_entries)}件")
        logger.info(f"科目区分の備考: {len(class_note_entries)}件")
        logger.info(f"科目名: {len(subject_name_entries)}件")
        logger.info(f"履修可能学年: {len(syllabus_eligible_grade_entries)}件")
        logger.info(f"入学年度制限: {len(syllabus_enrollment_year_entries)}件")
        logger.info(f"学部: {len(faculty_entries)}件")
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
        print("使用方法: python syllabus_list.py [年度]")
        sys.exit(1)
    
    process_syllabus_list_data(year) 