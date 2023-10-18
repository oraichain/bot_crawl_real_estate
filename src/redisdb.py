import redis


def client():
   # Kết nối tới máy chủ Redis
   redis_host = 'localhost'  # Thay thế bằng địa chỉ máy chủ Redis của bạn
   redis_port = 6379  # Thay thế bằng cổng Redis của bạn
   redis_password = None  # Thay thế bằng mật khẩu Redis của bạn nếu có
   redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


def check_id_crawl(id_crawl,set_name):
   # nếu id_crawl chưa tồn tại trong set_name trả về True
   if redisdb.sadd(set_name, id_crawl) == 1:
      return True
   else:
      return False

def delete_id_crawl(id_crawl,set_name):
   # xoá id_crawl trong set_name
   redisdb.srem(set_name, id_crawl)
   
def check_id_crawl_exist(id_crawl,set_name):
   # nếu id_crawl đã tồn tại trong set_name trả về True
   if redisdb.sismember(set_name, id_crawl) == 1:
      return True
   else:
      return False


   
   
   





