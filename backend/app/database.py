# database.py
import os
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL, echo=False)
Base = declarative_base()

class RealFinal(Base):
    __tablename__ = "realfinal"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    # Add category if you need category-based filtering:
    category = Column(String, nullable=True)

    business_hours = Column(Text, nullable=True)
    facilities = Column(Text, nullable=True)
    parking = Column(Text, nullable=True)
    very_good = Column(Text, nullable=True)
    seat_info = Column(Text, nullable=True)
    menu = Column(Text, nullable=True)

    # Additional columns from 'realfinal' or 'final':
    photo_url = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    connect_url = Column(Text, nullable=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Optional: create tables if missing
# Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    try:
        session = SessionLocal()
        # quick test
        count = session.query(RealFinal).count()
        print(f"'realfinal' table row count: {count}")
    except Exception as e:
        print("DB connection test failed:", e)
    finally:
        session.close()