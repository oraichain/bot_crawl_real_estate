import duckdb
import json


client = duckdb.connect('./duckdb/realestate.db')

# show tables raw
raw = client.execute("SELECT * FROM raw")

# get one row
row = raw.fetchone()
# convert to json
data_ = row[2]
print(data_)
