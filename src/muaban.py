import requests
from utils import logging, check_id_crawl, Duckdb
import hashlib

duckdb = Duckdb()

def getId(offset):
   url = f'https://muaban.net/listing/v1/classifieds/listing?subcategory_id=169&category_id=33&city_id=24&limit=20&offset={offset}'
   response = requests.get(url)
   if response.status_code == 200:
      list_id = []
      for item in response.json()['items']:
            list_id.append(item['id'])
      return list_id
   else:
      return None
   

def getJSON(id):
   url = f'https://muaban.net/listing/v1/classifieds/{id}/detail'
   response = requests.get(url)
   website = url.split("/")[2]  
   #return f"('{hashlib.md5(str(id).encode()).hexdigest()}', '{website}', '{response.text}')"
   return [hashlib.md5(str(id).encode()).hexdigest(), website, response.text]     

def run(offset):
   for i in range(offset,offset + 200,20):
         list_ids = getId(i)
         if list_ids != None:
            for id in list_ids:
               if check_id_crawl(hashlib.md5(str(id).encode()).hexdigest(),'raw') == True:
                  data = getJSON(id)
                  duckdb.insert_raw('raw',data)
                  logging(f"Crawled website: muaban.net, Id: {hashlib.md5(str(id).encode()).hexdigest()}")
   


import threading
threads = []
for i in range(30000, 60000,200):
   threads.append(threading.Thread(target=run, args=(i,)))
for thread in threads:
   thread.start()
for thread in threads:
   thread.join()
duckdb.close()
