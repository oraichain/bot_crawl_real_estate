import sys
sys.path.append('src')
from utils import logging, Duckdb
import redis
from dotenv import load_dotenv
load_dotenv()
import os

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
#duckdb = Duckdb()

def compare_set(set_name1,set_name2):
      set1 = redisdb.smembers(set_name1)
      set2 = redisdb.smembers(set_name2)
      set3 = set1.difference(set2)
      return set3
  
  
list_id = compare_set('raw','post_neststock_done')
print(len(list_id))

