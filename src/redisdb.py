import redis


def client():
   redis_host = 'localhost' 
   redis_port = 6379
   redis_password = None
   redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
   return redisdb


def check_id_crawl(id_crawl,set_name):
   # nếu id_crawl chưa tồn tại trong set_name trả về True
   client = client()
   status = client.sadd(set_name, id_crawl)
   client.close()
   if status == 1:
      return True
   else:
      return False


def delete_id_crawl(id_crawl,set_name):
   client.srem(set_name, id_crawl)
   client.close()
   
   
def check_id_crawl_exist(id_crawl,set_name):
   status = client.sismember(set_name, id_crawl)
   client.close()
   if status == 1:
      return True
   else:
      return False


   
   
   





