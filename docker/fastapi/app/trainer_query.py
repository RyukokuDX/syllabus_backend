from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import os
import subprocess
import tempfile
import re

router = APIRouter()

TRAINER_SQL_DIR = "/app/trainer/sql"
TRAINER_RESPONSE_DIR = "/app/trainer/response"

# 危険なキーワード・多重セミコロンの簡易バリデーション（JOIN LATERALやjsonb関数は許可）
def validate_sql_safe(sql: str):
	body = re.sub(r"--.*", "", sql)
	if ";" in body.strip()[:-1]:
		raise HTTPException(status_code=400, detail="複数SQL文は禁止です")
	forbidden = ["insert", "update", "delete", "drop", "alter", "create", "copy", "do", "execute"]
	for word in forbidden:
		if re.search(rf"\\b{word}\\b", body, re.IGNORECASE):
			raise HTTPException(status_code=400, detail=f"禁止キーワードが含まれています: {word}")

def validate_syllabus_cache_only(sql: str):
	for match in re.finditer(r"\\bFROM\\s+([a-zA-Z0-9_\.]+)|\\bJOIN\\s+([a-zA-Z0-9_\.]+)", sql, re.IGNORECASE):
		table = match.group(1) or match.group(2)
		# syllabus_cacheは許可
		if table.lower() == "syllabus_cache":
			continue
		# 関数呼び出し（例: jsonb_array_elements(...), lateral(...)）は許可
		if re.match(r"^[a-zA-Z0-9_]+\\s*\\(", table):
			continue
		raise HTTPException(status_code=400, detail=f"syllabus_cacheテーブル以外へのアクセスは禁止されています: {table}")

@router.post("/api/trainer_query/execute")
def execute_trainer_query(
	order: str = Form(...),
	desc: Optional[str] = Form(""),
	author: Optional[str] = Form("cursor"),
	file_name: Optional[str] = Form(None),
	sql_file: UploadFile = File(...)
):
	"""
	SQLファイルを受け取り、psqlで実行。結果（TSV）を返す。
	対象テーブルはsyllabus_cacheのみ許可。
	"""
	sql = sql_file.file.read().decode("utf-8")
	validate_sql_safe(sql)
	validate_syllabus_cache_only(sql)
	with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as tmp_sql:
		tmp_sql.write(sql)
		tmp_sql_path = tmp_sql.name
	try:
		env = os.environ.copy()
		env["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD", "")
		result = subprocess.run(
			["psql", "-U", os.getenv("POSTGRES_USER", "postgres"), "-d", os.getenv("POSTGRES_DB", "postgres"), "-h", os.getenv("POSTGRES_HOST", "postgres-db"), "-F", "\t", "--no-align", "-P", "footer=off", "-P", "null=''", "-f", tmp_sql_path],
			capture_output=True, text=True, timeout=10, env=env
		)
		if result.returncode != 0:
			raise HTTPException(status_code=400, detail=f"SQL実行エラー: {result.stderr}")
		return {"tsv": result.stdout}
	finally:
		os.remove(tmp_sql_path) 