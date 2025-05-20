import glob
from bs4 import BeautifulSoup

def process_subject_data(year):
    # シラバスのHTMLファイルを処理
    html_files = glob.glob(f"src/syllabus/{year}/raw_page/*.html")
    
    for html_file in html_files:
        with open(html_file, "r", encoding="utf-8") as f:
            html_content = f.read()
            
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 講義計画のテーブルを探す
        lecture_plan_table = soup.find("table", class_="kekaku_tbl")
        if not lecture_plan_table:
            print(f"Warning: 講義計画のテーブルが見つかりません: {html_file}")
            continue
            
        # ヘッダー行を探す
        header_row = lecture_plan_table.find("tr", class_="titles")
        if not header_row:
            print(f"Warning: ヘッダー行が見つかりません: {html_file}")
            continue
            
        # データ行を取得
        data_rows = lecture_plan_table.find_all("tr", class_="sub-data-nn")
        
        # hidden inputの値を取得
        hidden_inputs = lecture_plan_table.find_all("input", type="hidden")
        hidden_values = {input.get("name"): input.get("value") for input in hidden_inputs}
        
        # 各行のデータを処理
        for row in data_rows:
            # 回数
            lecture_num = row.find("td", class_="lecture").text.strip()
            
            # 担当者
            instructor = row.find("td", class_="instructor").text.strip()
            
            # 学修内容
            contents = row.find("td", class_="contents").text.strip()
            
            # hidden inputの値を各行に割り当て
            row_data = {
                "lecture_num": lecture_num,
                "instructor": instructor,
                "contents": contents,
                **hidden_values
            }
            
            # データを保存
            save_lecture_data(row_data) 