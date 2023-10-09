import requests
from bs4 import BeautifulSoup
import mongodb
from noti_logging import logging
import hashlib
import redisdb

mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')

def getPage(offset):
   if offset == 0 or offset ==1:
      url = 'https://alonhadat.com.vn/nha-dat/can-ban.html'
   else:
      url = f'https://alonhadat.com.vn/nha-dat/can-ban/trang--{offset}.html'
      
   response = requests.get(url)
   soup = BeautifulSoup(response.text, 'html.parser')
   links = soup.find_all('div', class_='ct_title')
   links = [link.find('a')['href'] for link in links]
   links = list(set(links))
   links = ['https://alonhadat.com.vn'+link for link in links]
   return links
   
def getHTML(url):
   response = requests.get(url)
   return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': 'alonhadat.com.vn', 'data': response.text}

def run(offset):
   for i in range(1, offset):
      links = getPage(offset)
      for link in links:
         if redisdb.check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
            data = getHTML(link)
            mongodb.insert(data)
            logging(f'Crawled website: alonhadat.com.vn, Id: {data["id_crawl"]}, Link: {link}')
   mongodb.close()
         
run(2)