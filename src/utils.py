# tạo hàm loggin để lưu lại các thông tin cần thiết và lưu vào file log đồng thời in ra màn hình
import os
from datetime import datetime
import requests
import time
from dotenv import load_dotenv
import redis
import duckdb
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
   with open('./src/proxy','r') as f:
      info_proxy = f.read().split('|')
      if info_proxy[0] == '':
         create_proxy()
         time.sleep(5)
         return get_proxy(time_live_proxy)
      if time.time() - float(info_proxy[1]) > time_live_proxy:
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
   
   
class Duckdb:
   def __init__(self):
      self.conn = duckdb.connect('./duckdb/realestate.db')
      self.c = self.conn.cursor()
      
   def insert_raw(self,tabel_name,data):
      query = f"""INSERT INTO {tabel_name} VALUES (?, ?, ?)"""
      self.c.execute(query, data)
      self.conn.commit()
      
   def insert_post_neststock(self,tabel_name,data):
      query = f"""INSERT INTO {tabel_name} VALUES (?, ?)"""
      self.c.execute(query, data)
      self.conn.commit()
      
      
   def create_table(self,table_name,columns):
      self.c.execute(f"""CREATE TABLE {table_name} {columns}""")
      self.conn.commit()
   def delete_table(self,table_name):
      self.c.execute(f"DROP TABLE {table_name}")
      self.conn.commit()
   def select(self,table_name,id_crawl):
      self.c.execute(f"SELECT * FROM {table_name} WHERE id_crawl = '{id_crawl}'")
      return self.c.fetchall()
   def select_many(self,table_name,id_crawls):
      self.c.execute(f"""SELECT * FROM {table_name} WHERE id_crawl IN ({id_crawls})""")
      return self.c.fetchall()
   
   
   def info_table(self,table_name):
      self.c.execute(f"SELECT * FROM {table_name}")
      return len(self.c.fetchall())
   
   def info_database(self):
      self.c.execute("SELECT name FROM sqlite_master WHERE type='table';")
      # return tung table trong database, moi table bao nhieu row
      info = {}
      for table in self.c.fetchall():
         self.c.execute(f"SELECT * FROM {table[0]}")
         info[table[0]] = len(self.c.fetchall())
      return info
   
   def delete_all(self,table_name):
      self.c.execute(f"DELETE FROM {table_name}")
      self.conn.commit()
   def close(self):
      self.conn.close()
      

