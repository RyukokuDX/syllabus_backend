import os
import json
from typing import List, Dict, Set
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
import re

def get_current_year() -> int:
    """現在の年度を取得する"""
    return datetime.now().year

def get_year_from_user() -> int:
    """ユーザーから年度を入力してもらう"""
    while True:
        try:
            year = input("年度を入力してください（空の場合は現在の年度）: ").strip()
            if not year:
                return get_current_year()
            year = int(year)
            if 2000 <= year <= 2100:  # 妥当な年度の範囲をチェック
                return year
            print("2000年から2100年の間で入力してください。")
        except ValueError:
            print("有効な数値を入力してください。")

def get_html_files(year: int) -> List[str]:
    """指定された年度のHTMLファイルのパスを取得する"""
    base_dir = os.path.join("src", "syllabus", str(year), "raw_html")
    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"ディレクトリが見つかりません: {base_dir}")
    
    html_files = [f for f in os.listdir(base_dir) if f.endswith('.html')]
    if not html_files:
        raise FileNotFoundError(f"HTMLファイルが見つかりません: {base_dir}")
    
    return [os.path.join(base_dir, f) for f in html_files]

def create_pretty_html(html_content: str, output_path: str) -> None:
    """HTMLを整形して保存する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    pretty_html = soup.prettify()
    
    # 出力ディレクトリの作成
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(pretty_html)

def find_th_with_text(soup: BeautifulSoup, text: str) -> BeautifulSoup:
    """指定されたテキストを含むthタグを探す"""
    for th in soup.find_all('th'):
        if text in th.text:
            return th
    return None

def get_next_td_content(element: BeautifulSoup) -> str:
    """指定された要素の次のtdタグの内容を取得する"""
    next_td = element.find_next('td')
    if not next_td:
        return ""
    return next_td.text.strip()

def extract_instructor_info(html_content: str, file_path: str) -> List[Dict]:
    """HTMLから教員情報を抽出する"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 教員情報を抽出
    instructors = []
    
    # 漢字氏名を抽出
    name_th = find_th_with_text(soup, '担当者Instructor漢字氏名')
    if not name_th:
        raise ValueError(f"担当者漢字氏名が見つかりません: {file_path}")
    name_content = get_next_td_content(name_th)
    if not name_content:
        raise ValueError(f"担当者漢字氏名の内容が見つかりません: {file_path}")
    
    # カナ氏名を抽出
    kana_th = find_th_with_text(soup, '担当者Instructorカナ氏名')
    if not kana_th:
        raise ValueError(f"担当者カナ氏名が見つかりません: {file_path}")
    kana_content = get_next_td_content(kana_th)
    if not kana_content:
        raise ValueError(f"担当者カナ氏名の内容が見つかりません: {file_path}")
    
    # カンマ区切りの教員名を取得
    names = [name.strip() for name in name_content.split(',')]
    kanas = [kana.strip() for kana in kana_content.split(',')]
    
    if len(names) != len(kanas):
        raise ValueError(f"漢字氏名とカナ氏名の数が一致しません: {file_path}")
    
    # 各教員の情報を抽出
    for name, kana in zip(names, kanas):
        # 姓と名を分割（空白で区切られていると仮定）
        name_parts = name.split()
        kana_parts = kana.split()
        
        if len(name_parts) < 2:
            raise ValueError(f"漢字氏名の形式が不正です: {file_path} - {name}")
        if len(kana_parts) < 2:
            raise ValueError(f"カナ氏名の形式が不正です: {file_path} - {kana}")
        
        instructor_info = {
            'last_name': name_parts[0],
            'first_name': ' '.join(name_parts[1:]),
            'last_name_kana': kana_parts[0],
            'first_name_kana': ' '.join(kana_parts[1:])
        }
        instructors.append(instructor_info)
    
    return instructors

def create_instructor_json(instructors: Set[Dict]) -> str:
    """教員情報のJSONファイルを作成する"""
    output_dir = os.path.join("updates", "instructor", "add")
    os.makedirs(output_dir, exist_ok=True)
    
    # 現在の日時を取得してファイル名を生成
    current_time = datetime.now()
    filename = f"instructor_{current_time.strftime('%Y%m%d_%H%M')}.json"
    output_file = os.path.join(output_dir, filename)
    
    data = {
        "instructors": [{
            "instructor_code": f"TEMP_{i:04d}",  # 一時的な教職員番号を生成
            "last_name": instructor["last_name"],
            "first_name": instructor["first_name"],
            "last_name_kana": instructor["last_name_kana"],
            "first_name_kana": instructor["first_name_kana"],
            "created_at": current_time.isoformat()
        } for i, instructor in enumerate(sorted(instructors, key=lambda x: (x["last_name_kana"], x["first_name_kana"])))]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return output_file

def main():
    """メイン処理"""
    try:
        # 年度の取得
        year = get_year_from_user()
        print(f"処理対象年度: {year}")
        
        # HTMLファイルの取得
        html_files = get_html_files(year)
        print(f"処理対象ファイル: {len(html_files)}件")
        
        # 教員情報の抽出
        all_instructors = set()
        for html_file in tqdm(html_files, desc="教員情報を抽出中"):
            try:
                # 元のHTMLファイルを読み込む
                with open(html_file, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # 整形したHTMLを保存
                pretty_html_path = html_file.replace('raw_html', 'pretty_html')
                create_pretty_html(html_content, pretty_html_path)
                
                # 整形したHTMLを読み込んで解析
                with open(pretty_html_path, 'r', encoding='utf-8') as f:
                    pretty_html_content = f.read()
                    instructors = extract_instructor_info(pretty_html_content, html_file)
                    # 各教員の情報をタプルに変換してセットに追加（重複を防ぐため）
                    for instructor in instructors:
                        instructor_tuple = tuple(sorted(instructor.items()))
                        all_instructors.add(instructor_tuple)
            except Exception as e:
                print(f"エラー: {html_file}の処理中にエラーが発生しました: {str(e)}")
                raise  # エラーを発生させて処理を停止
        
        # タプルを辞書に戻す
        instructor_dicts = [dict(t) for t in all_instructors]
        print(f"抽出された教員情報: {len(instructor_dicts)}件")
        
        # JSONファイルの作成
        output_file = create_instructor_json(instructor_dicts)
        print(f"JSONファイルを作成しました: {output_file}")
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        raise

if __name__ == "__main__":
    main() 