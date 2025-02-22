from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
# ✅ Database URL
DB_URL =  os.getenv("DB_URL")

# ✅ Create Engine
engine = create_engine(DB_URL)

# ✅ Test Connection
with engine.connect() as connection:
    result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for row in result:
        print(row)