from sqlalchemy import create_engine

# ✅ Database URL
DB_URL = "postgresql://neondb_owner:npg_JsRt76hDMPUF@ep-bitter-heart-a8s7lv10-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

# ✅ Create Engine
engine = create_engine(DB_URL)

# ✅ Test Connection
with engine.connect() as connection:
    result = connection.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
    for row in result:
        print(row)