# File Version: v2.7.1
# Project Version: v2.7.1
# Last Updated: 2025-07-06

from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_health import health
from loguru import logger
import os
import json
import time
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import DictCursor
from contextlib import contextmanager
from urllib.parse import urlparse

# 環境変数から設定を読み込み
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
CORS_ORIGINS = json.loads(os.getenv("CORS_ORIGINS", '["http://localhost:3000"]'))
CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# PostgreSQL接続設定（structure.mdの定義に準拠）
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@postgres-db:5432/syllabus_db")

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="シラバス情報API",
    description="龍谷大学のシラバス情報を提供するAPI",
    version="1.0.1",
    debug=DEBUG_MODE,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{API_PREFIX}/openapi.json"
)

# APIルーターの作成
router = APIRouter(prefix=API_PREFIX)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ロギングの設定
logger.add(
    "logs/api.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG" if DEBUG_MODE else "INFO"
)

# structure.mdに準拠した許可カラム定義
ALLOWED_COLUMNS = {
    "class": ["class_id", "class_name", "created_at"],
    "subclass": ["subclass_id", "subclass_name", "created_at"],
    "faculty": ["faculty_id", "faculty_name", "created_at"],
    "subject_name": ["subject_name_id", "name", "created_at"],
    "instructor": ["instructor_id", "name", "name_kana", "created_at"],
    "syllabus_master": ["syllabus_id", "syllabus_code", "syllabus_year", "created_at", "updated_at"],
    "book": ["book_id", "title", "author", "publisher", "price", "isbn", "created_at"],
    "book_uncategorized": ["id", "syllabus_id", "title", "author", "publisher", "price", "role", "isbn", "categorization_status", "created_at", "updated_at"],
    "syllabus": ["syllabus_id", "subject_name_id", "subtitle", "term", "campus", "credits", "goals", "summary", "attainment", "methods", "outside_study", "textbook_comment", "reference_comment", "grading_comment", "advice", "created_at", "updated_at"],
    "subject_grade": ["id", "syllabus_id", "grade", "created_at", "updated_at"],
    "lecture_time": ["id", "syllabus_id", "day_of_week", "period", "created_at", "updated_at"],
    "lecture_session": ["lecture_session_id", "syllabus_id", "session_number", "contents", "other_info", "lecture_format", "created_at", "updated_at"],
    "lecture_session_irregular": ["lecture_session_irregular_id", "syllabus_id", "session_pattern", "contents", "other_info", "instructor", "error_message", "lecture_format", "created_at", "updated_at"],
    "syllabus_instructor": ["id", "syllabus_id", "instructor_id", "role", "created_at", "updated_at"],
    "lecture_session_instructor": ["id", "lecture_session_id", "instructor_id", "role", "created_at", "updated_at"],
    "syllabus_book": ["id", "syllabus_id", "book_id", "role", "note", "created_at"],
    "grading_criterion": ["id", "syllabus_id", "criteria_type", "criteria_description", "ratio", "note", "created_at"],
    "subject_attribute": ["attribute_id", "attribute_name", "description", "created_at"],
    "subject": ["subject_id", "subject_name_id", "faculty_id", "curriculum_year", "class_id", "subclass_id", "requirement_type", "created_at", "updated_at"],
    "subject_attribute_value": ["id", "subject_id", "attribute_id", "value", "created_at", "updated_at"],
    "syllabus_faculty": ["id", "syllabus_id", "faculty_id", "created_at", "updated_at"],
    "syllabus_study_system": ["id", "source_syllabus_id", "target", "created_at", "updated_at"]
}

# 禁止されたSQLパターン
FORBIDDEN_PATTERNS = [
    r";(?!\s*$)",     # セミコロン（末尾のセミコロンは許可）
    r"(?i)INSERT",     # INSERT文
    r"(?i)UPDATE",     # UPDATE文
    r"(?i)DELETE",     # DELETE文
    r"(?i)DROP",       # DROP文
    r"(?i)CREATE",     # CREATE文
    r"(?i)ALTER",      # ALTER文
    r"(?i)TRUNCATE",   # TRUNCATE文
    r"(?i)ATTACH",     # ATTACH文
    r"(?i)DETACH",     # DETACH文
]

# 常に許可されるパターン（メタデータクエリ）
METADATA_PATTERNS = [
    r"^SELECT\s+column_name,\s*data_type\s+FROM\s+information_schema\.columns\s+WHERE\s+table_name\s*=\s*'[^']+'",  # テーブル情報
    r"^SELECT\s+table_name\s+FROM\s+information_schema\.tables\s+WHERE\s+table_schema\s*=\s*'public'",  # テーブル一覧
    r"^SELECT\s+constraint_name,\s*column_name\s+FROM\s+information_schema\.key_column_usage\s+WHERE\s+table_name\s*=\s*'[^']+'",  # 外部キー情報
]

# 疑わしいLIKEパターン
SUSPICIOUS_PATTERNS = [
    "%--",
    "%';",
    "%;",
    "%/*",
    "%*/",
    "%@@"
]

class QueryRequest(BaseModel):
    query: str = Field(..., description="実行するSQLクエリ")
    params: Optional[List[Any]] = Field(default=None, description="クエリパラメータ")

@contextmanager
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=DictCursor)
    try:
        yield conn
    finally:
        conn.close()

def validate_query(query: str, params: Optional[List[Any]] = None) -> None:
    # メタデータクエリの確認（常に許可）
    query_stripped = query.strip()
    for pattern in METADATA_PATTERNS:
        if re.match(pattern, query_stripped, re.IGNORECASE):
            return

    # SELECTで始まることを確認（メタデータクエリでない場合）
    if not re.match(r"^\s*SELECT", query, re.IGNORECASE):
        raise HTTPException(
            status_code=403,
            detail="Only SELECT queries and metadata queries are allowed"
        )
    
    # 禁止パターンのチェック
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, query):
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden SQL pattern detected"
            )
    
    # LIKEパターンの検証
    if params:
        for param in params:
            if isinstance(param, str):
                for pattern in SUSPICIOUS_PATTERNS:
                    if pattern in param:
                        logger.warning(f"Suspicious LIKE pattern detected: {param}")
                        raise HTTPException(
                            status_code=403,
                            detail="Suspicious LIKE pattern detected"
                        )

# ヘルスチェックエンドポイント
async def db_health_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

app.add_api_route("/health", health([db_health_check]))

# エラーハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.post(f"{API_PREFIX}/query")
async def execute_query(request: QueryRequest):
    start_time = time.time()
    
    try:
        # クエリの検証
        validate_query(request.query, request.params)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(request.query, request.params)
            results = cursor.fetchall()
            
            # 実行時間の計算
            execution_time = time.time() - start_time
            
            return {
                "results": results,
                "execution_time": execution_time,
                "row_count": len(results)
            }
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Query execution error: {str(e)}"
        )

# APIバージョン情報
@router.get("/version")
async def version():
    return {"version": "1.0.1"}

# ルーターをアプリケーションに登録
app.include_router(router)

# ルートエンドポイント
@app.get("/")
async def root():
    return {"message": "シラバス情報API サービス"}