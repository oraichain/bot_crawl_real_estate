from bs4 import BeautifulSoup
import requests
import mongodb
from utils import logging
import hashlib
import redisdb
mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')


def getPage(page):
   url = f'https://guland.vn/mua-ban-bat-dong-san?page={page}'
   payload={}
   headers = {
   'authority': 'guland.vn',
   'accept': 'text/html, */*; q=0.01',
   'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
   'cache-control': 'max-age=0'
   }
   response = requests.request("GET", url, headers=headers, data=payload)
   soup = BeautifulSoup(response.text, 'html.parser')
   links = soup.find_all('div', class_='c-sdb-card__tle')
   links = [link.a["href"] for link in links]
   return links
   
   
def getHTML(url):
   payload={}
   headers = {
   'authority': 'mogi.vn',
   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
   'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
   'cookie': 'UID=bbc08ff3-6555-430a-a664-34d08b247e13; _gcl_au=1.1.1821714249.1693211206; _gid=GA1.2.859459221.1693211206; _fbp=fb.1.1693211206549.2104283531; __gads=ID=91164ce46772351f-2229e7ee50e3000b:T=1693216290:RT=1693216290:S=ALNI_MZ8b1YqoPo8NZfSOnmAicA61d5eqw; __gpi=UID=00000c35190772a5:T=1693216290:RT=1693216290:S=ALNI_MZUyZlXy1Ao_llYUwEyBOago6Oulw; _ga_EPTMT9HK3X=GS1.1.1693214628.2.1.1693216313.28.0.0; _ga=GA1.2.1441087283.1693211206',
   'referer': 'https://mogi.vn/mua-nha-dat',
   'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
   'sec-ch-ua-mobile': '?0',
   'sec-ch-ua-platform': '"macOS"',
   'sec-fetch-dest': 'document',
   'sec-fetch-mode': 'navigate',
   'sec-fetch-site': 'same-origin',
   'sec-fetch-user': '?1',
   'upgrade-insecure-requests': '1',
   'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
   }
   response = requests.request("GET", url, headers=headers, data=payload)
   return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': 'guland.vn', 'data': response.text}


def run(offset):
   for page in range(1, offset):
      links = getPage(page)
      for link in links:
         if redisdb.check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
            data = getHTML(link)
            mongodb.insert(data)
            logging(f'Crawled website: guland.vn, Id: {data["id_crawl"]}, Link: {link}')
   mongodb.close()
run(2)
         
       
