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

sys.path.append('src')
from utils import logging, Duckdb
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
duckdb = Duckdb()


def compare_set(set_name1,set_name2):
      set1 = redisdb.smembers(set_name1)
      set2 = redisdb.smembers(set_name2)
      set3 = set1.difference(set2)
      return set3




def etl_thread(data):
    website_handlers = {
    'nhatot.com': nhatot.transferNhatot,
    'muaban.net': muaban.transferMuaban,
    'batdongsan.com.vn': batdongsan.transferBatdongsan,
    'guland.vn': guland.transferGuland,
    'cafeland.vn': cafeland.transferCafeland,
    'meeyland.com': meeyland.transferMeeyland,
    }
      
    website = data['website']
    if website in website_handlers:
            dataTransfer = website_handlers[website](data['data'])
            if dataTransfer is not None:
                dataUpdate = [data['id_crawl'],dataTransfer]
                duckdb.insert_post_neststock('post_neststock',dataUpdate)
                redisdb.sadd('post_neststock', data['id_crawl'])
                logging(f'Đã chuyển dữ liệu từ {website} sang neststock thành công')
            else:
                redisdb.sadd('post_neststock_reject', data['id_crawl'])
    else:
            redisdb.sadd('post_neststock_reject', data['id_crawl'])
            logging(f'Reject ID: {data["id_crawl"]} - Website: {website}',level='error')

            
     
            

                  
     
            
                        
while True:
    id_crawl_no_reject = compare_set('raw','post_neststock_reject')
    id_crawl = compare_set('raw','post_neststock')
    list_id_crawl = id_crawl_no_reject.intersection(id_crawl)
    logging(f'Số lượng bài viết cần chuyển: {len(list_id_crawl)}')
        
    list_id_crawl = list(list_id_crawl)

    if len(list_id_crawl) > 100:
        list_id_crawl = list_id_crawl[:100]

    list_id_crawl = ', '.join([f"'{id_crawl}'" for id_crawl in list_id_crawl])
    datas = duckdb.select_many('raw',list_id_crawl)
    datas = [{'id_crawl':data[0],'website':data[1],'data':data[2]} for data in datas]
   
    map = Pool(30)
    map.map(etl_thread,datas)
    map.close()
    map.join()
    
    break
      
