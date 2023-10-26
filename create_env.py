import duckdb

client = duckdb.connect('./duckdb/realestate.db')
client.execute('CREATE TABLE raw (id_crawl VARCHAR(50), website VARCHAR(50), data TEXT)')
client.execute('CREATE TABLE post_neststock (id_crawl VARCHAR(50), data TEXT)')
client.close()