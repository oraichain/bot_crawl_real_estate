import os
import redis
def client():
   redis_host = 'localhost' 
   redis_port = 6379
   redis_password = None
   redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
   return redisdb


xpath = './data/raw/batdongsan.com.vn'

# get list name file in folder
list_name_file = os.listdir(xpath)

print(len(list_name_file))


client().sadd('raw_s1',*list_name_file)
