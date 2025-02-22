import psycopg2
import pandas as pd
import ast
import json

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ Load CSV File
df = pd.read_csv("SQL_DB.csv")

# ✅ Convert columns to correct data types
df["facilities"] = df["facilities"].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df["menu"] = df["menu"].apply(lambda x: json.loads(x) if isinstance(x, str) else {})


# # ✅ Use the correct password
conn = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),  # ✅ Double-check your password!
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    sslmode="require"  # ✅ This ensures a secure connection
)

print("✅ Connected to NeonDB!")
cur = conn.cursor()

# ✅ SQL Query to Insert Data
insert_query = """
INSERT INTO reviews (id, size, road_address, name, category, latitude, longitude, phone, business_hours, review_count, facilities, parking, very_good, seat_info, menu)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (name) DO NOTHING;
"""


# ✅ Upload Each Row from CSV
for idx, row in df.iterrows():
    cur.execute(insert_query, (
        row["id"],
        row["size"],
        row["road_address"],
        row["name"],
        row["category"],
        row["latitude"],
        row["longitude"],
        row["phone"],
        row["business_hours"],
        row["review_count"],
        row["facilities"],
        row["parking"],
        row["very_good"],
        row["seat_info"],
        json.dumps(row["menu"]) 
    ))


# ✅ Commit & Close
conn.commit()
cur.close()
conn.close()

print("✅ Data uploaded successfully to NeonDB!")