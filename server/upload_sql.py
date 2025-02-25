import psycopg2
import pandas as pd
import ast
import json

from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ Load CSV File
df = pd.read_csv("final_link_sql.csv")

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
INSERT INTO realfinal (id, size, road_address, name, category, latitude, longitude, phone, business_hours, review_count, facilities, parking, very_good, seat_info, menu, photo_url, connect_url)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        row["menu"],
        row["photo_url"],
        row["connect_url"]
    ))


# ✅ Commit & Close
conn.commit()
cur.close()
conn.close()

print("✅ Data uploaded successfully to NeonDB!")