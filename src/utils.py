# tạo hàm loggin để lưu lại các thông tin cần thiết và lưu vào file log đồng thời in ra màn hình
import os
from datetime import datetime
import requests
import time
from dotenv import load_dotenv
import redis
load_dotenv()



def logging(message, level='info'):
      # lưu vào file log
      # lấy thời gian hiện tại
      now = datetime.now()
      # lấy tên file hiện tại
      filename = os.path.basename(__file__)
      # tạo đường dẫn đến file log theo ngày
      log_file = f'logs/{now.strftime("%Y-%m-%d")}.log'
      # tạo đường dẫn đến thư mục logs
      log_dir = os.path.dirname(log_file)
      # kiểm tra nếu thư mục logs chưa tồn tại thì tạo mới
      if not os.path.exists(log_dir):
         os.makedirs(log_dir)
      # tạo nội dung log
      content = f'{now.strftime("%d/%m/%Y %H:%M:%S")} - {level.upper()} - {message}'
      # lưu vào file log
      with open(log_file, 'a') as f:
         f.write(content + '\n')
      # in ra màn hình
      print(content)
      
      
def create_proxy():
    TINSOFT_KEY = os.getenv('TINSOFT_KEY')
    url = f'https://proxy.tinsoftsv.com/api/changeProxy.php?key={TINSOFT_KEY}'
    response = requests.get(url)
    proxy = response.json()
    if proxy['success'] == True:
        with open('./src/proxy','w') as f:
            f.write(f'{proxy["proxy"]}|{time.time()}')
    else:
        time.sleep(proxy['next_change']+1)
        return create_proxy()
     

def get_proxy(time_live_proxy):
   TIME_LIVE_PROXY = 20*60
   with open('./src/proxy','r') as f:
      info_proxy = f.read().split('|')
      if info_proxy[0] == '':
         create_proxy()
         time.sleep(5)
         return get_proxy(time_live_proxy)
      if time.time() - float(info_proxy[1]) > TIME_LIVE_PROXY:
         create_proxy()
         time.sleep(5)
         return get_proxy(time_live_proxy)
      else:
         return info_proxy[0]
      

def client():
   redis_host = 'localhost' 
   redis_port = 6379
   redis_password = None
   redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
   return redisdb


def check_id_crawl(id_crawl,set_name):
   # nếu id_crawl chưa tồn tại trong set_name trả về True
   client_ = client()
   status = client_.sadd(set_name, id_crawl)
   client_.close()
   if status == 1:
      return True
   else:
      return False


def delete_id_crawl(id_crawl,set_name):
   client_ = client()
   client_.srem(set_name, id_crawl)
   client_.close()
   
   
def check_id_crawl_exist(id_crawl,set_name):
   client_ = client()
   status = client_.sismember(set_name, id_crawl)
   client_.close()
   if status == 1:
      return True
   else:
      return False
      
