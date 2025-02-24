# debug_db.py
from app.database import SessionLocal, RealFinal  # FastAPI에서 세션 및 모델 가져오기

session = SessionLocal()
print("DEBUG: RealFinal 테이블 컬럼 목록 ->", RealFinal.__table__.columns.keys())

restaurants = session.query(RealFinal).limit(5).all()
print("DEBUG: 샘플 데이터 ->", [(r.id, r.category, r.business_hours) for r in restaurants])
session.close()