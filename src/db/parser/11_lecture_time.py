# File Version: v1.3.0
# Project Version: v1.3.18
# Last Updated: 2025/6/21

import os
import json
import sys
from typing import List, Dict
from datetime import datetime
import re
from tqdm import tqdm
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import unicodedata

# ���ߤΥǥ��쥯�ȥ��Python�ѥ����ɲ�
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# utils.py�����������ؿ��򥤥�ݡ���
try:
	from utils import normalize_subject_name
except ImportError:
	# utils.py�����Ĥ���ʤ����Υե�����Хå�
	def normalize_subject_name(text: str) -> str:
		"""�ƥ����Ȥ�����������ʥե�����Хå���"""
		return unicodedata.normalize('NFKC', text)

def get_db_connection():
	"""�ǡ����١�����³���������"""
	# �Ķ��ѿ�������³��������
	user = os.getenv('POSTGRES_USER', 'postgres')
	password = os.getenv('POSTGRES_PASSWORD', 'postgres')
	host = os.getenv('POSTGRES_HOST', 'localhost')
	port = os.getenv('POSTGRES_PORT', '5432')
	db = os.getenv('POSTGRES_DB', 'syllabus_db')

	# ��³ʸ��������
	connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db}"
	
	# ���󥸥�����
	engine = create_engine(
		connection_string,
		connect_args={
			'options': '-c client_encoding=utf-8'
		}
	)
	
	# ���å��������
	Session = sessionmaker(bind=engine)
	session = Session()
	
	# ���å����������˰��٤���ʸ�����󥳡��ǥ��󥰤�����
	session.execute(text("SET client_encoding TO 'utf-8'"))
	session.commit()
	
	return session

def get_syllabus_master_id_from_db(session, syllabus_code: str, syllabus_year: int) -> int:
	"""����Х��ޥ�����ID���������"""
	try:
		# ����Х��ޥ�����ID�����
		query = text("""
			SELECT syllabus_id 
			FROM syllabus_master 
			WHERE syllabus_code = :code 
			AND syllabus_year = :year
		""")
		
		result = session.execute(
			query,
			{"code": syllabus_code, "year": syllabus_year}
		).first()
		
		return result[0] if result else None
	except Exception as e:
		session.rollback()
		return None

def get_current_year() -> int:
	"""���ߤ�ǯ�٤��������"""
	return datetime.now().year

def get_year_from_user() -> int:
	"""�桼��������ǯ�٤����Ϥ��Ƥ�餦"""
	while True:
		try:
			year = input("ǯ�٤����Ϥ��Ƥ��������ʶ��ξ��ϸ��ߤ�ǯ�١�: ").strip()
			if not year:
				return get_current_year()
			year = int(year)
			if 2000 <= year <= 2100:  # ������ǯ�٤��ϰϤ�����å�
				return year
			print("2000ǯ����2100ǯ�δ֤����Ϥ��Ƥ���������")
		except ValueError:
			print("ͭ���ʿ��ͤ����Ϥ��Ƥ���������")

def parse_lecture_time(time_text: str) -> List[Dict]:
	"""�ֵ����֥ƥ����Ȥ���Ϥ��������Ȼ��¤���Ф���"""
	lecture_times = []
	
	if not time_text:
		return lecture_times
	
	# ����ֵ��ξ��
	if '����' in time_text:
		lecture_times.append({
			'day_of_week': '����',
			'period': 0
		})
		return lecture_times
	
	# �̾�ιֵ����֤����
	# ��: "��� �売(Y019)" �� ������2��
	# ��: "���� ����壳" �� ������1�¡�������3��
	# ��: "���� �ڣ�(YJ11)���ڣ��ʥڥ���" �� ������4�¡�������5��
	
	# �����Υޥåԥ�
	day_mapping = {
		'��': '��',
		'��': '��', 
		'��': '��',
		'��': '��',
		'��': '��',
		'��': '��',
		'��': '��'
	}
	
	# utils.py����������ǽ����Ѥ������ѿ�����Ⱦ�Ѥ��Ѵ�
	time_text_normalized = normalize_subject_name(time_text)
	
	# ʣ���λ��¤�ʬ��ʡ��Ƕ��ڤ��Ƥ������
	time_parts = time_text_normalized.split('')  # ���������줿������ʬ��
	
	for part in time_parts:
		part = part.strip()
		if not part:
			continue
		
		# �����Ȼ��¤Υѥ�����򸡺�
		# �ѥ�����: ���� + ������1-6�¡�
		pattern = r'([��п��ڶ�����])([1-6])'
		matches = re.findall(pattern, part)
		
		for day_char, period_str in matches:
			if day_char in day_mapping:
				lecture_times.append({
					'day_of_week': day_mapping[day_char],
					'period': int(period_str)
				})
	
	# �ޥå����ʤ����ϡ��ƥ��������Τ򤽤Τޤ޻���
	if not lecture_times and time_text.strip():
		lecture_times.append({
			'day_of_week': time_text.strip(),
			'period': 0
		})
	
	return lecture_times

def get_json_files(year: int) -> List[str]:
	"""���ꤵ�줿ǯ�٤Τ��٤Ƥ�JSON�ե�����Υѥ����������"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	if not os.path.exists(json_dir):
		raise FileNotFoundError(f"�ǥ��쥯�ȥ꤬���Ĥ���ޤ���: {json_dir}")
	
	json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
	if not json_files:
		raise FileNotFoundError(f"JSON�ե����뤬���Ĥ���ޤ���: {json_dir}")
	
	return [os.path.join(json_dir, f) for f in json_files]

def extract_lecture_time_from_single_json(json_data: Dict, session, year: int) -> List[Dict]:
	"""ñ���JSON�ե����뤫��ֵ����־������Ф���"""
	lecture_times = []
	
	# ���ܥ����ɤ����
	syllabus_code = json_data.get("���ܥ�����", "")
	
	# ���ִ����˹ֻ������
	basic_info = json_data.get("���ܾ���", {})
	time_info = basic_info.get("���ִ����˹ֻ�", {})
	time_text = time_info.get("����", "") if isinstance(time_info, dict) else str(time_info)
	
	if time_text and syllabus_code:
		# syllabus_master����syllabus_id�����
		syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
		
		if syllabus_id:
			# �ֵ����֤����
			parsed_times = parse_lecture_time(time_text)
			for time_data in parsed_times:
				lecture_times.append({
					'syllabus_id': syllabus_id,
					'day_of_week': time_data['day_of_week'],
					'period': time_data['period']
				})
	
	return lecture_times

def process_lecture_time_json(json_file: str, session, year: int) -> tuple[List[Dict], List[str]]:
	"""���̤ιֵ�����JSON�ե�������������"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# �ֵ����־�������
		lecture_times = extract_lecture_time_from_single_json(json_data, session, year)
		
		if not lecture_times:
			errors.append("�ֵ����־��󤬸��Ĥ���ʤ�����syllabus_master���б�����쥳���ɤ�����ޤ���")
		
		return lecture_times, errors
		
	except json.JSONDecodeError as e:
		errors.append(f"JSON�ե�����β��ϥ��顼: {str(e)}")
		return [], errors
	except Exception as e:
		errors.append(f"������˥��顼��ȯ��: {str(e)}")
		return [], errors

def create_lecture_time_json(lecture_times: List[Dict]) -> str:
	"""�ֵ����־����JSON�ե�������������"""
	output_dir = os.path.join("updates", "lecture_time", "add")
	os.makedirs(output_dir, exist_ok=True)
	
	# ���ߤ�������������ƥե�����̾������
	current_time = datetime.now()
	filename = f"lecture_time_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(output_dir, filename)
	
	data = {
		"lecture_times": [{
			"syllabus_id": time["syllabus_id"],
			"day_of_week": time["day_of_week"],
			"period": time["period"],
			"created_at": current_time.isoformat()
		} for time in sorted(lecture_times, key=lambda x: (x["syllabus_id"], x["day_of_week"], x["period"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def main():
	"""�ᥤ�����"""
	session = None
	try:
		# ǯ�٤μ���
		year = get_year_from_user()
		print(f"�����о�ǯ��: {year}")
		
		# �ǡ����١�����³
		session = get_db_connection()
		
		# ���٤Ƥ�JSON�ե���������
		json_files = get_json_files(year)
		print(f"�����оݥե������: {len(json_files)}")
		
		# �ֵ����־�������
		all_lecture_times = []
		processed_count = 0
		error_count = 0
		skipped_count = 0
		
		# ���顼��������
		all_errors = []
		
		# ���׾���
		stats = {
			"total_files": len(json_files),
			"successful_files": 0,
			"error_files": 0,
			"total_lecture_times": 0
		}
		
		print(f"\n��������: {len(json_files)}�Ĥ�JSON�ե�����")
		
		# tqdm����Ѥ��ƥץ��쥹�С���ɽ��
		for json_file in tqdm(json_files, desc="JSON�ե�����������"):
			try:
				# ���̤�JSON�ե���������
				lecture_times, errors = process_lecture_time_json(json_file, session, year)
				
				if lecture_times:
					all_lecture_times.extend(lecture_times)
					processed_count += len(lecture_times)
					stats["successful_files"] += 1
					stats["total_lecture_times"] += len(lecture_times)
				else:
					skipped_count += 1
					stats["error_files"] += 1
				
				# ���顼��������
				if errors:
					for error in errors:
						all_errors.append(f"{os.path.basename(json_file)}: {error}")
					
			except Exception as e:
				error_count += 1
				stats["error_files"] += 1
				all_errors.append(f"{os.path.basename(json_file)}: ������˥��顼��ȯ��: {str(e)}")
				continue
		
		print(f"\n�������:")
		print(f"- ��ե������: {stats['total_files']}")
		print(f"- �����ե������: {stats['successful_files']}")
		print(f"- ���顼�ե������: {stats['error_files']}")
		print(f"- ��ֵ����ֿ�: {stats['total_lecture_times']}")
		print(f"- ����: {processed_count}��")
		print(f"- ���顼: {error_count}��")
		print(f"- �����å�: {skipped_count}��")
		
		# ���顼�����ޤȤ��ɽ��
		if all_errors:
			print(f"\n���顼�ܺ� ({len(all_errors)}��):")
			print("=" * 80)
			for i, error in enumerate(all_errors, 1):
				print(f"{i:3d}. {error}")
			print("=" * 80)
		
		# JSON�ե�����κ���
		if all_lecture_times:
			output_file = create_lecture_time_json(all_lecture_times)
			print(f"\nJSON�ե������������ޤ���: {output_file}")
		else:
			print("\n������ǽ�ʹֵ����֥ǡ��������Ĥ���ޤ���Ǥ�����")
		
	except Exception as e:
		print(f"���顼��ȯ�����ޤ���: {str(e)}")
		print(f"���顼�μ���: {type(e)}")
		raise
	finally:
		if session:
			session.close()

if __name__ == "__main__":
	main() 