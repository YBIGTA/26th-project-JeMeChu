## db랑 연결하는 파일
import psycopg2 # pip install psycopg2-binary
from psycopg2.extras import DictCursor
import json
import os
from dotenv import load_dotenv

load_dotenv() # .env 파일 로딩

# 환경 변수에서 DATABASE_URL 가져오기
DB_URL = os.getenv("DATABASE_URL")
print(DB_URL[:5]) # debugging(지우기)

def get_db_connection():
    """
    PostgreSQL DB 연결을 생성하는 함수
    """
    try:
        conn = psycopg2.connect(DB_URL, cursor_factory=DictCursor)  # DictCursor 사용하여 결과를 딕셔너리처럼 다룸
        return conn
    except Exception as e:
        print("!!DB 연결 실패:", e)
        return None

# debugging(아래 함수 지우기)
if __name__ == "__main__":
    conn = get_db_connection()

    if conn: 
        print("db 연결 굿")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'restaurant_updated';
            """)
            columns = cursor.fetchall()

            print("restaurant_updated 테이블의 컬럼명:")
            for col in columns:
                print("-", col[0])  # 컬럼명 출력

        except Exception as e:
            print("컬럼 조회 실패:", e)
        finally:
            cursor.close()
            conn.close()
    else:
        print("db 연결 실패..")
