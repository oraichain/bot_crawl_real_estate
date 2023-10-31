import sys
sys.path.append('crawl')
from utils import logging
import redis
from dotenv import load_dotenv
load_dotenv()
import os
import requests
import json
import time
redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
API_KEY_NESTSTOCK_POST = os.getenv('API_KEY_NESTSTOCK_POST')


def compare_set(set_name1,set_name2):
      set1 = redisdb.smembers(set_name1)
      set2 = redisdb.smembers(set_name2)
      set3 = set1.difference(set2)
      return set3
  
   
def postNeststock(data):
   data = json.loads(data)
   #data['propertyBasicInfo']['contact']['phoneNumber']['value'] = ' '
   url = "https://backend.neststock.orai.us/properties/ai-crawl"
   payload = json.dumps(data)
   headers = {
   'x-crawler-key': API_KEY_NESTSTOCK_POST,
   'Content-Type': 'application/json'
   }
   response = requests.request("POST", url, headers=headers, data=payload)
   if 'data' not in response.json():
      print(response.json())
      return False
   
   if 'propertyDataSource' in response.json()['data']:
      return True
   else:
      return False

def run(id):
      with open(f'data/post/batdongsan.com.vn/{id}','r') as f:
            data = f.read()
      status = postNeststock(data)
      if status == True:
            redisdb.sadd('neststock_s1_done',id)
            logging(f'Posted website: batdongsan.com.vn, Id: {id}')
      else:
            redisdb.sadd('neststock_s1_reject',id)
            logging(f'Failed to post website: batdongsan.com.vn, Id: {id}')
            
list_id = compare_set('neststock_s1','neststock_s1_done')
list_id_reject = compare_set('neststock_s1_reject','none')
list_id = list(list_id)
list_id_reject = list(list_id_reject)
list_id = list(set(list_id).difference(set(list_id_reject)))


#list_id = list_id[0:5000]
import threading
threads = []
for id in list_id:
      t = threading.Thread(target=run, args=(id,))
      threads.append(t)
for thread in threads:
      thread.start()
      time.sleep(0.1)
for thread in threads:
      thread.join()
      

      
      
