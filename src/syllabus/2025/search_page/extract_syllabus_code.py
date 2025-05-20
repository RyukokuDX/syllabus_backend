import os
from bs4 import BeautifulSoup
import re

def extract_syllabus_codes(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    # param_syllabusKanriNoフィールドからシラバス管理番号を抽出
    syllabus_field = soup.find('input', {'name': 'param_syllabusKanriNo'})
    if syllabus_field and syllabus_field.get('value'):
        # カンマ区切りの値を分割して重複を除去
        codes = list(set(syllabus_field['value'].split(',')))
        return codes
    
    return []

def main():
    # 検索結果ページのディレクトリ
    search_dir = 'src/syllabus/2025/search_page'
    
    # 出力ファイル
    output_file = 'src/syllabus/2025/syllabus_codes.txt'
    
    # シラバス管理番号を格納するセット
    syllabus_codes = set()
    
    # 検索結果ページを処理
    for filename in os.listdir(search_dir):
        if filename.startswith('search_results_') and filename.endswith('.html'):
            html_file = os.path.join(search_dir, filename)
            codes = extract_syllabus_codes(html_file)
            syllabus_codes.update(codes)
    
    # 結果をファイルに出力
    with open(output_file, 'w', encoding='utf-8') as f:
        for code in sorted(syllabus_codes):
            f.write(f'{code}\n')
    
    print(f'抽出されたシラバス管理番号の数: {len(syllabus_codes)}')

if __name__ == '__main__':
    main() 