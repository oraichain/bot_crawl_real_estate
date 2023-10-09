import requests
import mongodb
import requests
from bs4 import BeautifulSoup
from noti_logging import logging
import redisdb
import hashlib

mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')

def crawlNewFeed():
   url = 'https://meeyland.com/_next/data/UhjJMW6d8mnHNjkYS53eE/mua-ban-nha-dat.json?filter=need%5B%5D%3Dcan_ban&sort=0&category=mua-ban-nha-dat'
   response = requests.get(url)
   if response.status_code != 200:
      return crawlNewFeed()
   data = response.json()
   data = data['pageProps']['fallback']
   return data[list(data.keys())[0]]['data']


def run():
   list_ids = crawlNewFeed()
   for item in list_ids:
      if redisdb.check_id_crawl(hashlib.md5(item['_id'].encode()).hexdigest(),'raw') == True:
         data = {'id_crawl': hashlib.md5(item['_id'].encode()).hexdigest(), 'website': 'meeyland.com', 'data': item}
         mongodb.insert(data)
         logging(f'Crawled website: meeyland.com, Id: {data["id_crawl"]}')
         
run()