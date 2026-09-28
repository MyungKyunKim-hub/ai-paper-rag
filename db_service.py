import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def save_qa(question, answer):
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="rag_db",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO qa_history (question, answer)
        VALUES (%s, %s)
        """,
        (question, answer)
    )

    conn.commit()

    cursor.close()
    conn.close()

def get_history():
    conn = psycopg.connect(
        host="localhost",
        port=5432,
        dbname="rag_db",
        user="postgres",
        password=os.getenv("POSTGRES_PASSWORD")
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, question, answer, created_at
        FROM qa_history
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows