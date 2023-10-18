import requests
from bs4 import BeautifulSoup
import mongodb
from utils import logging, check_id_crawl
import hashlib

mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')


def getNewFeed():
   url = 'https://sosanhnha.com/nh%C3%A0-%C4%91%E1%BA%A5t-b%C3%A1n'
   response = requests.get(url)
   soup = BeautifulSoup(response.text, 'html.parser')
   
   links = soup.find_all('a', class_='img_r')
   links = [link['href'] for link in links]
   link = list(set(links))
   link = ['https://sosanhnha.com'+link for link in link]
   return link
   
   
def getHTML(url):
   response = requests.get(url)
   return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': 'sosanhnha.com', 'data': response.text}


def run():
   links = getNewFeed()
   for link in links:
      if check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
         data = getHTML(link)
         mongodb.insert(data)
         logging(f'Crawled website: sosanhnha.com, Id: {data["id_crawl"]}, Link: {link}')
   mongodb.close()
   
run()