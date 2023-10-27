import requests
import requests
from bs4 import BeautifulSoup
from utils import logging, check_id_crawl, Duckdb
import hashlib

duckdb = Duckdb()

global PUBLIC_KEY
with open('./src/public_key_meeyland', 'r') as f:
   PUBLIC_KEY = f.read()
def get_key():
   url = 'https://meeyland.com/mua-ban-nha-dat'
   response = requests.get(url)
   if response.status_code != 200:
      return get_key()
   soup = BeautifulSoup(response.text, 'html.parser')
   scripts = soup.find_all('script')
   for script in scripts:
      if '_buildManifest.js' in str(script.get('src')):
         return script.get('src').split('/')[5]
      

def getPage(page):
   url = f'https://meeyland.com/_next/data/auCKEsBYknvyDVbN4jix0/mua-ban-nha-dat/ha-noi.json?page={page}&category=mua-ban-nha-dat&slug=ha-noi'
   response = requests.get(url)
   if response.status_code != 200:
      return getPage(page)
   data = response.json()
   data = data['pageProps']['fallback']
   return data[list(data.keys())[0]]['data']


def run(page):
   list_ids = getPage(page)
   print(f'Get page: {page}')
   for item in list_ids:
      if check_id_crawl(hashlib.md5(item['_id'].encode()).hexdigest(),'raw') == True:
         data = [hashlib.md5(item['_id'].encode()).hexdigest(), 'meeyland.com', item]
         duckdb.insert_raw('raw',data)
         logging(f"Crawled website: meeyland.com, Id: {hashlib.md5(item['_id'].encode()).hexdigest()}")
   
   
import threading
threads = []
for i in range(435, 1000,1):
   run(i)
duckdb.close()