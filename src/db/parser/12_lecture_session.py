# -*- coding: utf-8 -*-
# File Version: v1.3.1
# Project Version: v1.3.21
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
import csv

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

def parse_lecture_sessions_from_schedule(schedule_data: List[Dict]) -> tuple[List[Dict], List[Dict]]:
	"""�ֵ��ײ��schedule���󤫤�ֵ�����ǡ�������Ϥ��ƹ�¤������
	�̾�ιֵ������������ֵ������ʬ�����֤�"""
	import re  # �ؿ�����Ƭ�ǥ���ݡ���
	
	lecture_sessions = []  # �̾�ιֵ������1-15���
	lecture_sessions_irregular = []  # ������ֵ����
	
	if not schedule_data:
		return lecture_sessions, lecture_sessions_irregular
	
	for session_data in schedule_data:
		if not isinstance(session_data, dict):
			continue
		
		# ������������: "1-1" �� 1, "2-2" �� 2, "1����" �� 1��
		session = session_data.get("session", "")
		if not session:
			continue
		
		# utils.py����������ǽ����Ѥ�������ʸ����Ⱦ�Ѥ��Ѵ�
		session_normalized = normalize_subject_name(session)
		
		# ����ʸ�������ʿ����ʳ�������ʸ��������
		session_cleaned = re.sub(r'[^\d\-]', '', session_normalized)
		
		# �ǥХå���: ������������ͤ��ǧ
		# print(f"DEBUG: session='{session}' -> normalized='{session_normalized}' -> cleaned='{session_cleaned}'")
		
		# ���Ƥ����
		contents = session_data.get("content", "")
		
		# ô���Ծ���������lecture_session_instructor�ơ��֥��ѡ�
		instructor = session_data.get("instructor", "")
		
		# ����ѥ������ʬ��
		session_pattern = session  # ���Υѥ�������ݻ�
		
		# �ޤ��ֲ��ܡ׷���������å�
		if '����' in session_normalized:
			# ���������
			numbers = re.findall(r'\d+', session_normalized)
			if numbers:
				try:
					session_number = int(numbers[0])
					# 1-15����ϰ��⤫�����å�
					if 1 <= session_number <= 15:
						# �̾�ιֵ�����Ȥ��ƽ���
						lecture_sessions.append({
							'session_number': session_number,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
					else:
						# �ϰϳ��ξ���������Ȥ��ƽ���
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# �����Ѵ��Ǥ��ʤ�����������Ȥ��ƽ���
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			else:
				# ���������Ĥ���ʤ�����������Ȥ��ƽ���
				lecture_sessions_irregular.append({
					'session_pattern': session_pattern,
					'contents': contents if contents else None,
					'other_info': None,
					'instructor': instructor if instructor else None
				})
		else:
			# �ϥ��ե���ڤ�η���������å�
			session_parts = session_cleaned.split('-')
			if len(session_parts) >= 2:
				try:
					start_session = int(session_parts[0])
					end_session = int(session_parts[1])
					
					# �ϰϤ�1-15����ǡ�Ϣ³���Ƥ�������̾�ιֵ�����Ȥ��ƽ���
					if (1 <= start_session <= 15 and 1 <= end_session <= 15 and 
						end_session >= start_session and end_session - start_session <= 14):
						# �ϰ���Τ��٤Ƥβ��������
						for session_number in range(start_session, end_session + 1):
							lecture_sessions.append({
								'session_number': session_number,
								'contents': contents if contents else None,
								'other_info': None,
								'instructor': instructor if instructor else None
							})
					else:
						# �ϰϳ��ޤ�����Ϣ³�ξ���������Ȥ��ƽ���
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# �����Ѵ��Ǥ��ʤ�����������Ȥ��ƽ���
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			elif len(session_parts) == 1:
				try:
					session_number = int(session_parts[0])
					# 1-15����ϰ��⤫�����å�
					if 1 <= session_number <= 15:
						# �̾�ιֵ�����Ȥ��ƽ���
						lecture_sessions.append({
							'session_number': session_number,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
					else:
						# �ϰϳ��ξ���������Ȥ��ƽ���
						lecture_sessions_irregular.append({
							'session_pattern': session_pattern,
							'contents': contents if contents else None,
							'other_info': None,
							'instructor': instructor if instructor else None
						})
				except ValueError:
					# �����Ѵ��Ǥ��ʤ�����������Ȥ��ƽ���
					lecture_sessions_irregular.append({
						'session_pattern': session_pattern,
						'contents': contents if contents else None,
						'other_info': None,
						'instructor': instructor if instructor else None
					})
			else:
				# ͭ���ʷ����Ǥʤ�����������Ȥ��ƽ���
				lecture_sessions_irregular.append({
					'session_pattern': session_pattern,
					'contents': contents if contents else None,
					'other_info': None,
					'instructor': instructor if instructor else None
				})
	
	# print(f"DEBUG: Total lecture_sessions created: {len(lecture_sessions)}")
	# print(f"DEBUG: Total lecture_sessions_irregular created: {len(lecture_sessions_irregular)}")
	return lecture_sessions, lecture_sessions_irregular

def get_json_files(year: int) -> List[str]:
	"""���ꤵ�줿ǯ�٤Τ��٤Ƥ�JSON�ե�����Υѥ����������"""
	json_dir = os.path.join("src", "syllabus", str(year), "json")
	if not os.path.exists(json_dir):
		raise FileNotFoundError(f"�ǥ��쥯�ȥ꤬���Ĥ���ޤ���: {json_dir}")
	
	json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
	if not json_files:
		raise FileNotFoundError(f"JSON�ե����뤬���Ĥ���ޤ���: {json_dir}")
	
	return [os.path.join(json_dir, f) for f in json_files]

def extract_lecture_session_from_single_json(json_data: Dict, session, year: int) -> tuple[List[Dict], List[Dict], List[str]]:
	"""ñ���JSON�ե����뤫��ֵ�����������Ф���
	�̾�ιֵ������������ֵ������ʬ�����֤�"""
	lecture_sessions = []  # �̾�ιֵ����
	lecture_sessions_irregular = []  # ������ֵ����
	errors = []
	
	# ���ܥ����ɤ����
	syllabus_code = json_data.get("���ܥ�����", "")
	
	if not syllabus_code:
		errors.append("���ܥ����ɤ����Ĥ���ޤ���")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# syllabus_master����syllabus_id�����
	syllabus_id = get_syllabus_master_id_from_db(session, syllabus_code, year)
	
	if not syllabus_id:
		errors.append(f"syllabus_master���б�����쥳���ɤ�����ޤ���ʲ��ܥ�����: {syllabus_code}��")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# �ֵ��ײ�����
	lecture_plan = json_data.get("�ֵ��ײ�", {})
	schedule_data = lecture_plan.get("����", {})
	
	if isinstance(schedule_data, dict):
		schedule = schedule_data.get("schedule", [])
	else:
		schedule = []
	
	if not schedule:
		errors.append("�ֵ��ײ��schedule�����Ĥ���ޤ���")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# �ֵ���������
	parsed_sessions, parsed_sessions_irregular = parse_lecture_sessions_from_schedule(schedule)
	
	if not parsed_sessions and not parsed_sessions_irregular:
		errors.append("�ֵ�����β��Ϸ�̤����Ǥ�")
		return lecture_sessions, lecture_sessions_irregular, errors
	
	# �̾�ιֵ���������
	for session_data in parsed_sessions:
		lecture_sessions.append({
			'syllabus_id': syllabus_id,
			'session_number': session_data['session_number'],
			'contents': session_data['contents'],
			'other_info': session_data['other_info'],
			'instructor': session_data['instructor']
		})
	
	# ������ֵ���������
	for session_data in parsed_sessions_irregular:
		lecture_sessions_irregular.append({
			'syllabus_id': syllabus_id,
			'session_pattern': session_data['session_pattern'],
			'contents': session_data['contents'],
			'other_info': session_data['other_info'],
			'instructor': session_data['instructor']
		})
	
	# ����ֵ����ɤ���������å�
	basic_info = json_data.get("���ܾ���", {})
	time_info = basic_info.get("���ִ����˹ֻ�", {})
	time_text = time_info.get("����", "") if isinstance(time_info, dict) else str(time_info)
	
	# ����ֵ��Ǥʤ���硢�ǽ��������å����̾�ιֵ�����Τߡ�
	if time_text and '����' not in time_text:
		if lecture_sessions:
			max_session = max(session['session_number'] for session in lecture_sessions)
			if max_session not in [15, 30]:
				errors.append(f"�ǽ���{max_session}��ʴ�����: 15��ޤ���30���")
	
	return lecture_sessions, lecture_sessions_irregular, errors

def process_lecture_session_json(json_file: str, session, year: int) -> tuple[List[Dict], List[Dict], List[str]]:
	"""���̤ιֵ����JSON�ե�������������
	�̾�ιֵ������������ֵ������ʬ�����֤�"""
	errors = []
	try:
		with open(json_file, 'r', encoding='utf-8') as f:
			json_data = json.load(f)
		
		# �ֵ������������
		lecture_sessions, lecture_sessions_irregular, extraction_errors = extract_lecture_session_from_single_json(json_data, session, year)
		
		# ��Х��顼���ɲ�
		errors.extend(extraction_errors)
		
		# ���顼���ʤ���������
		if not errors and (lecture_sessions or lecture_sessions_irregular):
			return lecture_sessions, lecture_sessions_irregular, []
		
		# ���顼��������Ͼܺ٤�Ͽ
		if errors:
			return [], [], errors
		
		# �ֵ�������󤬶��ξ��
		return [], [], ["�ֵ����������ФǤ��ޤ���Ǥ���"]
		
	except json.JSONDecodeError as e:
		errors.append(f"JSON�ե�����β��ϥ��顼: {str(e)}")
		return [], [], errors
	except Exception as e:
		errors.append(f"������˥��顼��ȯ��: {str(e)}")
		return [], [], errors

def create_lecture_session_json(lecture_sessions: List[Dict]) -> str:
	"""�ֵ���������JSON�ե�������������"""
	# lecture_session�ѤΥǥ��쥯�ȥ�
	session_output_dir = os.path.join("updates", "lecture_session", "add")
	os.makedirs(session_output_dir, exist_ok=True)
	
	# ���ߤ�������������ƥե�����̾������
	current_time = datetime.now()
	
	# lecture_session�Ѥ�JSON�ե�����
	filename = f"lecture_session_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(session_output_dir, filename)
	
	data = {
		"lecture_sessions": [{
			"syllabus_id": session["syllabus_id"],
			"session_number": session["session_number"],
			"contents": session["contents"],
			"other_info": session["other_info"],
			"created_at": current_time.isoformat()
		} for session in sorted(lecture_sessions, key=lambda x: (x["syllabus_id"], x["session_number"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def create_lecture_session_irregular_json(lecture_sessions_irregular: List[Dict]) -> str:
	"""������ֵ���������JSON�ե�������������"""
	# lecture_session_irregular�ѤΥǥ��쥯�ȥ�
	session_output_dir = os.path.join("updates", "lecture_session_irregular", "add")
	os.makedirs(session_output_dir, exist_ok=True)
	
	# ���ߤ�������������ƥե�����̾������
	current_time = datetime.now()
	
	# lecture_session_irregular�Ѥ�JSON�ե�����
	filename = f"lecture_session_irregular_{current_time.strftime('%Y%m%d_%H%M')}.json"
	output_file = os.path.join(session_output_dir, filename)
	
	data = {
		"lecture_session_irregulars": [{
			"syllabus_id": session["syllabus_id"],
			"session_pattern": session["session_pattern"],
			"contents": session["contents"],
			"other_info": session["other_info"],
			"created_at": current_time.isoformat()
		} for session in sorted(lecture_sessions_irregular, key=lambda x: (x["syllabus_id"], x["session_pattern"]))]
	}
	
	with open(output_file, 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)
	
	return output_file

def create_error_csv(all_errors: List[str], final_session_errors: List[str], year: int) -> str:
	"""���顼���Ƥ�CSV�ե�����Ȥ��ƽ��Ϥ���"""
	warning_dir = os.path.join("warning", str(year))
	os.makedirs(warning_dir, exist_ok=True)
	
	# ���ߤ�������������ƥե�����̾������
	current_time = datetime.now()
	filename = f"lecture_session_{current_time.strftime('%Y%m%d_%H%M')}.csv"
	output_file = os.path.join(warning_dir, filename)
	
	# ���顼���������
	error_data = []
	
	# �̾泌�顼�����
	for error in all_errors:
		# ���顼��å���������JSON�ե�����̾�����
		if ": " in error:
			json_name, error_message = error.split(": ", 1)
		else:
			json_name = "unknown"
			error_message = error
		
		error_data.append({
			'json_name': json_name,
			'error_message': error_message,
			'date': current_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	
	# �ǽ��󥨥顼�����
	for error in final_session_errors:
		# ���顼��å���������JSON�ե�����̾�����
		if ": " in error:
			json_name, error_message = error.split(": ", 1)
		else:
			json_name = "unknown"
			error_message = error
		
		error_data.append({
			'json_name': json_name,
			'error_message': error_message,
			'date': current_time.strftime('%Y-%m-%d %H:%M:%S')
		})
	
	# CSV�ե�����˽񤭹���
	with open(output_file, 'w', newline='', encoding='utf-8') as f:
		writer = csv.DictWriter(f, fieldnames=['json_name', 'error_message', 'date'])
		writer.writeheader()
		writer.writerows(error_data)
	
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
		
		# �ֵ������������
		all_lecture_sessions = []  # �̾�ιֵ����
		all_lecture_sessions_irregular = []  # ������ֵ����
		processed_count = 0
		error_count = 0
		skipped_count = 0
		
		# ���顼��������
		all_errors = []
		final_session_errors = []  # �ǽ��󥨥顼�����Ӽ���
		
		# ���׾���
		stats = {
			"total_files": len(json_files),
			"successful_files": 0,
			"error_files": 0,
			"total_lecture_sessions": 0,
			"total_lecture_sessions_irregular": 0,
			"final_session_error_files": 0
		}
		
		print(f"\n��������: {len(json_files)}�Ĥ�JSON�ե�����")
		
		# tqdm����Ѥ��ƥץ��쥹�С���ɽ��
		for json_file in tqdm(json_files, desc="JSON�ե�����������"):
			try:
				lecture_sessions, lecture_sessions_irregular, errors = process_lecture_session_json(json_file, session, year)
				
				# �ǽ��󥨥顼��ʬΥ
				final_session_error = None
				other_errors = []
				for error in errors:
					if "�ǽ���" in error:
						final_session_error = error
					else:
						other_errors.append(error)
				
				if other_errors:
					all_errors.extend([f"{os.path.basename(json_file)}: {error}" for error in other_errors])
					error_count += 1
					stats["error_files"] += 1
				else:
					if lecture_sessions or lecture_sessions_irregular:
						all_lecture_sessions.extend(lecture_sessions)
						all_lecture_sessions_irregular.extend(lecture_sessions_irregular)
						processed_count += 1
						stats["successful_files"] += 1
						stats["total_lecture_sessions"] += len(lecture_sessions)
						stats["total_lecture_sessions_irregular"] += len(lecture_sessions_irregular)
					else:
						skipped_count += 1
				
				# �ǽ��󥨥顼��Ͽ
				if final_session_error:
					final_session_errors.append(f"{os.path.basename(json_file)}: {final_session_error}")
					stats["final_session_error_files"] += 1
						
			except Exception as e:
				error_msg = f"{os.path.basename(json_file)}: ͽ�����ʤ����顼: {str(e)}"
				all_errors.append(error_msg)
				error_count += 1
				stats["error_files"] += 1
		
		# ��̤�ɽ��
		print(f"\n������λ:")
		print(f"  ����: {processed_count}�ե�����")
		print(f"  ���顼: {error_count}�ե�����")
		print(f"  �����å�: {skipped_count}�ե�����")
		print(f"  ��Ф��줿�̾�ֵ����: {len(all_lecture_sessions)}��")
		print(f"  ��Ф��줿������ֵ����: {len(all_lecture_sessions_irregular)}��")
		print(f"  �ǽ��󥨥顼: {stats['final_session_error_files']}�ե�����")
		
		# ���顼���������ɽ��
		if all_errors:
			print(f"\n���顼�ܺ� ({len(all_errors)}��):")
			for error in all_errors[:10]:  # �ǽ��10��Τ�ɽ��
				print(f"  - {error}")
			if len(all_errors) > 10:
				print(f"  ... ¾ {len(all_errors) - 10}��Υ��顼")
		
		# �ǽ��󥨥顼�ꥹ�Ȥ�ɽ��
		if final_session_errors:
			print(f"\n�ǽ��󥨥顼�ꥹ�� ({len(final_session_errors)}��):")
			for error in final_session_errors:
				print(f"  - {error}")
		
		# �̾�ιֵ�������󤬤������JSON�ե���������
		if all_lecture_sessions:
			output_file = create_lecture_session_json(all_lecture_sessions)
			print(f"\n�̾�ιֵ�����������¸���ޤ���: {output_file}")
		
		# ������ֵ�������󤬤������JSON�ե���������
		if all_lecture_sessions_irregular:
			output_file = create_lecture_session_irregular_json(all_lecture_sessions_irregular)
			print(f"\n������ֵ�����������¸���ޤ���: {output_file}")
		
		# ���׾����ɽ��
		if all_lecture_sessions or all_lecture_sessions_irregular:
			print(f"\n���׾���:")
			print(f"  �����оݥե������: {stats['total_files']}")
			print(f"  �����ե������: {stats['successful_files']}")
			print(f"  ���顼�ե������: {stats['error_files']}")
			print(f"  �ǽ��󥨥顼�ե������: {stats['final_session_error_files']}")
			print(f"  ��Ф��줿�̾�ֵ�������: {stats['total_lecture_sessions']}")
			print(f"  ��Ф��줿������ֵ�������: {stats['total_lecture_sessions_irregular']}")
		else:
			print("\n�ֵ�������󤬸��Ĥ���ޤ���Ǥ�����")
		
		# ���顼���Ƥ�CSV�ե�����Ȥ��ƽ���
		error_csv_file = create_error_csv(all_errors, final_session_errors, year)
		print(f"\n���顼���Ƥ�CSV�ե�����Ȥ��ƽ��Ϥ��ޤ���: {error_csv_file}")
		
	except FileNotFoundError as e:
		print(f"���顼: {e}")
	except KeyboardInterrupt:
		print("\n���������Ǥ���ޤ�����")
	except Exception as e:
		print(f"ͽ�����ʤ����顼��ȯ�����ޤ���: {e}")
	finally:
		if session:
			session.close()

if __name__ == "__main__":
	main() 