import psycopg2

try:
    conn = psycopg2.connect(
        dbname="neondb",
        user="neondb_owner",
        password="your-password",
        host="ep-bitter-heart-a8s7lv10-pooler.eastus2.azure.neon.tech",
        port="5432",
        sslmode="require"
    )
    print("✅ Connection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")