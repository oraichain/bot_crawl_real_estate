import requests
import mongodb
from utils import logging
import hashlib
import redisdb

mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')


def getId(offset):
   url = f'https://muaban.net/listing/v1/classifieds/listing?subcategory_id=169&category_id=33&sort=1&limit=20&offset={offset}'
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
   return {'id_crawl': hashlib.md5(str(id).encode()).hexdigest(), 'website': website, 'data': response.text}
         

def run(offset):
   for i in range(0,offset,20):
         list_ids = getId(i)
         if list_ids != None:
            for id in list_ids:
               if redisdb.check_id_crawl(hashlib.md5(str(id).encode()).hexdigest(),'raw') == True:
                  data = getJSON(id)
                  mongodb.insert(data)
                  logging(f"Crawled website: muaban.net, Id: {data['id_crawl']}")
   mongodb.close()  
   
     
run(40)
               
               
