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
      

def crawlNewFeed(PUBLIC_KEY):
   url = f'https://meeyland.com/_next/data/{PUBLIC_KEY}/mua-ban-nha-dat/ha-noi.json?filter=city%5B%5D%3D5e5501caeb80a7245175dddb%26need%5B%5D%3Dcan_ban&page=2&sort=0&category=mua-ban-nha-dat&slug=ha-noi'
   response = requests.get(url)
   if response.status_code != 200:
      PUBLIC_KEY = get_key()
      return crawlNewFeed(PUBLIC_KEY)
   data = response.json()
   data = data['pageProps']['fallback']
   return data[list(data.keys())[0]]['data']


def run():
   list_ids = crawlNewFeed(PUBLIC_KEY)
   for item in list_ids:
      if check_id_crawl(hashlib.md5(item['_id'].encode()).hexdigest(),'raw') == True:
         data = [hashlib.md5(item['_id'].encode()).hexdigest(), 'meeyland.com', item]
         duckdb.insert_raw('raw',data)
         logging(f"Crawled website: meeyland.com, Id: {hashlib.md5(item['_id'].encode()).hexdigest()}")
   duckdb.close()
   
run()