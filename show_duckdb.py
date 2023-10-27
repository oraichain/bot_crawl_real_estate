import duckdb
import json


client = duckdb.connect('./duckdb/realestate.db')

# show tables raw
raw = client.execute("SELECT * FROM raw")

# dem so luong ban ghi

print(len(raw.fetchall()))