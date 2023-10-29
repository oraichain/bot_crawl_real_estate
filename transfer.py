import redis
import sys
from multiprocessing import Pool
sys.path.append('transfer')
import nhatot
import muaban
import batdongsan
import guland
import cafeland
import meeyland

sys.path.append('crawl')
from utils import logging
import json
import time
import threading
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()



redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)


def compare_set(set_name1,set_name2):
      set1 = redisdb.smembers(set_name1)
      set2 = redisdb.smembers(set_name2)
      set3 = set1.difference(set2)
      return set3

def save(s,id,data):
    with open(f'data/post/{s}/{id}','w') as f:
        f.write(data)

data_s1 = list(compare_set('raw_s1','neststock_s1'))
data_s1_reject = list(compare_set('neststock_s1_reject','none'))
data_s1 = list(set(data_s1).difference(set(data_s1_reject)))

#print(f'Number of data: {len(data_s1)}')

def etl_s1(id):
    try:
        with open('data/raw/batdongsan.com.vn/'+id,'r') as f:
            data = f.read()
    except:
        redisdb.srem('raw_s1',id)
        logging(f'Deleted website: batdongsan.com.vn, Id: {id}')
        return None
    data_transfer = batdongsan.transferBatdongsan(data)
    if data_transfer != None:
        data_transfer = json.dumps(data_transfer)
        redisdb.sadd('neststock_s1',id)
        save('batdongsan.com.vn',id,data_transfer)
        logging(f'Transfered website: batdongsan.com.vn, Id: {id}')
    else:
        redisdb.sadd('neststock_s1_reject',id)
        logging(f'Rejected website: batdongsan.com.vn, Id: {id}')


def testcase_address(id):
    with open('data/raw/batdongsan.com.vn/'+id,'r') as f:
        data = f.read()
    address = batdongsan.title(data)
    with open('testcase.txt','a') as f:
        f.write(f'{address}\n----------------------------------\n')

    
map = Pool(20)
map.map(etl_s1,data_s1)
map.close()
map.join()
    

    
      
