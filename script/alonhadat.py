import requests
from bs4 import BeautifulSoup
import hashlib
import sys
sys.path.append('..')
from src.save_data import save
with open('proxy.txt', 'r') as f:
   proxy = f.read()
   
   
def getPage(offset):
   if offset == 0 or offset ==1:
      url = 'https://alonhadat.com.vn/nha-dat/can-ban.html'
   else:
      url = f'https://alonhadat.com.vn/nha-dat/can-ban/trang--{offset}.html'
      
   response = requests.get(url, proxies={'https': proxy})
   soup = BeautifulSoup(response.text, 'html.parser')
   links = soup.find_all('div', class_='ct_title')
   links = [link.find('a')['href'] for link in links]
   links = list(set(links))
   links = ['https://alonhadat.com.vn'+link for link in links]
   return links
   
def getHTML(url):
   response = requests.get(url, proxies={'https': proxy})
   return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': 'alonhadat.com.vn', 'data': response.text}

def run(offset):
   for i in range(1, offset):
      links = getPage(offset)
      for link in links:
         data = getHTML(link)
         save(data['id_crawl'], data['data'], data['website'])
         
run(3)