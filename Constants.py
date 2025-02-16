import os

# 최상위 폴더의 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# database 폴더의 절대 경로 설정
DATABASE_PATH = os.path.abspath(os.path.join(BASE_DIR, "database"))

