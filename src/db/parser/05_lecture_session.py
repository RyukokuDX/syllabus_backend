from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import json
import re

@dataclass
class LectureSession:
    session_id: str
    syllabus_code: str
    day_of_week: str
    day_of_week_en: str
    period: str
    period_en: str
    room: str
    room_en: str
    created_at: datetime
    updated_at: datetime

class LectureSessionParser:
    @staticmethod
    def parse(raw_data: Dict[str, Any]) -> Optional[LectureSession]:
        try:
            return LectureSession(
                session_id=raw_data.get('session_id', ''),
                syllabus_code=raw_data.get('syllabus_code', ''),
                day_of_week=raw_data.get('day_of_week', ''),
                day_of_week_en=raw_data.get('day_of_week_en', ''),
                period=raw_data.get('period', ''),
                period_en=raw_data.get('period_en', ''),
                room=raw_data.get('room', ''),
                room_en=raw_data.get('room_en', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            print(f"Error parsing lecture session data: {e}")
            return None

def parse_syllabus_time(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    try:
        # シラバス管理番号を取得
        syllabus_code = None
        syllabus_id_table = soup.find('table', id='s_kanri_bango')
        if syllabus_id_table:
            syllabus_id_td = syllabus_id_table.find('td', class_='data-n0')
            if syllabus_id_td:
                syllabus_code = syllabus_id_td.get_text(strip=True)

        if not syllabus_code:
            print("  No syllabus ID found.")
            return []

        # 開講期と時間割情報を取得
        time_slots = []
        term_elem = soup.find('th', string=lambda x: x and '開講期' in x)
        if term_elem:
            term_td = term_elem.find_next('td')
            if term_td:
                term_text = term_td.get_text(strip=True)
                
                # 時間割情報を抽出（例：火３(Y119)・火４（ペア）など）
                # 曜日と時限のパターンを抽出
                time_pattern = r'([月火水木金土日])([１-５])'
                time_matches = list(re.finditer(time_pattern, term_text))
                
                # 時間割情報を処理
                i = 0
                while i < len(time_matches):
                    current_match = time_matches[i]
                    day_char = current_match.group(1)
                    period_char = current_match.group(2)
                    
                    # 曜日と時限を数値に変換
                    day_map = {'月': '月曜日', '火': '火曜日', '水': '水曜日', '木': '木曜日', '金': '金曜日', '土': '土曜日', '日': '日曜日'}
                    period_map = {'１': '1限', '２': '2限', '３': '3限', '４': '4限', '５': '5限'}
                    
                    day_of_week = day_map[day_char]
                    day_of_week_en = f"{day_char}day"
                    period = period_map[period_char]
                    period_en = f"Period {period_char}"
                    
                    # 現在の時限の前後のテキストを取得
                    current_pos = current_match.start()
                    next_pos = current_match.end()
                    after_text = term_text[next_pos:next_pos+20]
                    before_text = term_text[max(0, current_pos-20):current_pos]

                    # 教室情報を取得
                    room = ''
                    room_en = ''
                    room_match = re.search(r'\(([^)]+)\)', term_text[current_pos:current_pos+20])
                    if room_match:
                        room = room_match.group(1)
                        room_en = room

                    # エントリーを作成
                    entry = {
                        "session_id": f"{syllabus_code}_{day_char}{period_char}",
                        "syllabus_code": syllabus_code,
                        "day_of_week": day_of_week,
                        "day_of_week_en": day_of_week_en,
                        "period": period,
                        "period_en": period_en,
                        "room": room,
                        "room_en": room_en,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": None
                    }
                    time_slots.append(entry)
                    i += 1

        return time_slots

    except Exception as e:
        print(f"  Error parsing syllabus time: {str(e)}")
        return []

def save_json(entry: Dict[str, Any], year: str) -> None:
    session_id = entry["session_id"]
    out_dir = f"updates/lecture_session/add"
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, f"{session_id}.json")
    
    json_data = {
        "content": entry
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {filepath}")

def parse_html_file(filepath: str) -> List[Dict[str, Any]]:
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 整形されたHTMLを初回のみ保存（多重保存を防ぐ）
    pretty_path = filepath.replace('.pretty.html', '') + '.pretty.html'
    if not os.path.exists(pretty_path):
        with open(pretty_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

    return parse_syllabus_time(soup) 