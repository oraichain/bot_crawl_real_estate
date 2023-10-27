import requests
from bs4 import BeautifulSoup
from utils import logging, check_id_crawl, Duckdb
import hashlib

duckdb = Duckdb()


def getPage(page):
   url = 'https://sosanhnha.com/search?iCat=0&iCitId=9278&iDisId=0&iWardId=0&iPrice=0&keyword=&page={page}'
   response = requests.get(url)
   soup = BeautifulSoup(response.text, 'html.parser')
   links = soup.find_all('a', class_='name')
   links = [link['href'] for link in links]
   link = list(set(links))
   link = ['https://sosanhnha.com'+link for link in link]
   return link
   
   
def getHTML(url):
   response = requests.get(url)
   return [hashlib.md5(url.encode()).hexdigest(), 'sosanhnha.com', response.text]


def run(page):
   for number_page in range(1, page):
      links = getPage(number_page)
      for link in links:
         if check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
            data = getHTML(link)
            duckdb.insert_raw('raw',data)
            logging(f'Crawled website: sosanhnha.com, Id: {hashlib.md5(link.encode()).hexdigest()}')
      duckdb.close()
   
lists_page = [i for i in range(1, 1000)]
from multiprocessing import Pool
map = Pool(20).map
map(run,lists_page)
map.close()
map.join()