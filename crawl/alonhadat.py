import requests
from bs4 import BeautifulSoup
from utils import logging, get_proxy, check_id_crawl, Duckdb
import hashlib


duckdb = Duckdb()
   
PROXY = get_proxy(5*60)

def getPage(offset):
   if offset == 0 or offset ==1:
      url = 'https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi.html'
   else:
      url = f'https://alonhadat.com.vn/nha-dat/can-ban/nha-dat/1/ha-noi/trang--{offset}.html'
      
   response = requests.get(url, proxies={'https': PROXY})
   soup = BeautifulSoup(response.text, 'html.parser')
   links = soup.find_all('div', class_='ct_title')
   links = [link.find('a')['href'] for link in links]
   links = list(set(links))
   links = ['https://alonhadat.com.vn'+link for link in links]
   return links
   
def getHTML(url):
   response = requests.get(url, proxies={'https': PROXY})
   return [hashlib.md5(url.encode()).hexdigest(),'alonhadat.com.vn',response.text]

def run(offset):
   for i in range(1, offset):
      links = getPage(offset)
      for link in links:
         if check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
            data = getHTML(link)
            duckdb.insert_raw('raw',data)
            logging(f'Crawled website: alonhadat.com.vn, Id: {hashlib.md5(link.encode()).hexdigest()}')
   duckdb.close()

run(50)