import requests
import mongodb
from utils import logging
import hashlib
import redisdb

mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')


def getJSON(id):
   categorys = [1010,1020,1040,1030] # thêm 1050 nếu là cả thuê trọ
   url = f'https://gateway.chotot.com/v1/public/ad-listing/{id}'
   response = requests.get(url)
   if response.status_code == 200:
      try:
         if response.json()['ad']['category'] in categorys:
            return {'id_crawl': hashlib.md5(str(id).encode()).hexdigest(), 'website': 'nhatot.com', 'data': response.json()}
         else:
            return None
      except:
         return None
   else:
      return None
   

def crawlNewFeed():
   list_ids = []
   url = 'https://gateway.chotot.com/v1/public/ad-listing?limit=100&cg=1000'
   response = requests.get(url)
   categorys = [1010,1020,1040,1030]
   if response.status_code == 200:
      for item in response.json()['ads']:
         if item['category'] in categorys and item['type'] == 's':
            list_ids.append(item['list_id'])
      
      return list_ids
   else:
      return crawlNewFeed()


def run():
   list_ids = crawlNewFeed()
   for id in list_ids:
      if redisdb.check_id_crawl(hashlib.md5(str(id).encode()).hexdigest(),'raw') == True:
         data = getJSON(id)
         if data:
            mongodb.insert(data)
            logging(f'Crawled website: nhatot.com, Id: {data["id_crawl"]}')
   mongodb.close()
   
run()
   