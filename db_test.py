import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

print("비밀번호 로드 여부:", bool(os.getenv("POSTGRES_PASSWORD")))

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="rag_db",
    user="postgres",
    password=os.getenv("POSTGRES_PASSWORD")
)

print("PostgreSQL 연결 성공!")

cursor = conn.cursor()

cursor.execute(
    """
    INSERT INTO qa_history (question, answer)
    VALUES (%s, %s)
    """,
    ("Python에서 저장한 질문", "Python에서 저장한 답변")
)

conn.commit()

cursor.close()
conn.close()

print("데이터 저장 성공!")