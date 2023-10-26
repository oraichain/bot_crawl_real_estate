redis-cli DEL raw
redis-cli DEL post_neststock
redis-cli DEL post_neststock_reject
rm -rf ./duckdb/realestate.db
python3 create_env.py