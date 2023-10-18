import requests
from utils import logging, check_id_crawl, MongoDB, get_proxy
import hashlib
import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import threading

mongodb = MongoDB('tindangbatdongsan', 'raw')
PROXY = get_proxy(2*60)

def create_driver(page):         
    options = uc.ChromeOptions()
    # tắt load ảnh
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-notifications")
    options.add_argument('--proxy-server='+PROXY)
    driver = uc.Chrome(options=options,headless=False,version_main=117)
    driver.set_window_size(320, 360)
    driver.set_window_position((page-1)//3*320, (page-1)%3*360)
    return driver


def getPage(driver,page):
      if page == 1 or page == 0:
         url = 'https://www.nhatot.com/mua-ban-bat-dong-san'
      else:
         url = f'https://www.nhatot.com/mua-ban-bat-dong-san?page={page}'
      driver.set_page_load_timeout(10)
      try:
         driver.get(url)
      except:
         return []
      time.sleep(1)
      html = driver.page_source
      soup = BeautifulSoup(html, 'html.parser')
      # lấy tất cả link trong trang
      ids = soup.find_all('a', class_='AdItem_adItem__gDDQT')
      ids = [link['href'] for link in ids]
      ids = [link.split('/')[-1] for link in ids]
      ids = [id.split('.')[0] for id in ids]
      return ids


def getJSON(id):
   categorys = [1010,1020,1040,1030] # thêm 1050 nếu là cả thuê trọ
   url = f'https://gateway.chotot.com/v1/public/ad-listing/{id}'
   response = requests.get(url)
   if response.status_code == 200:
      try:
         if response.json()['ad']['category'] in categorys:
            return {'id_crawl': hashlib.md5(id.encode()).hexdigest(), 'website': 'nhatot.com', 'data': response.json()}
         else:
            return None
      except:
         return None
   else:
      return None
   
def crawl_one_thread(page):
   driver = create_driver(page)
   ids = getPage(driver,page)
   driver.quit()
   for id in ids:
      if check_id_crawl(hashlib.md5(str(id).encode()).hexdigest(),'raw') == True:
         data = getJSON(id)
         if data:
            mongodb.insert(data)
            logging(f'Crawled website: nhatot.com, Id: {data["id_crawl"]}')


def process():
   threads = []
   for i in range(1, 10):
      threads.append(threading.Thread(target=crawl_one_thread, args=(i,)))
   for thread in threads:
      thread.start()
      time.sleep(5)
   for thread in threads:
      thread.join()
   mongodb.close()


if __name__ == '__main__':
   process()