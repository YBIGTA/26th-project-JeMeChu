import pandas as pd

df = pd.read_csv("embedded_data.csv", encoding="utf-8-sig")

df = df[["id","embedding"]]

df.to_csv("embedding_data.csv", encoding="utf-8-sig",index=False)