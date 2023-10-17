import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import hashlib
import threading
import mongodb
from noti_logging import logging
import redisdb
import requests
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
load_dotenv()
import os
mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')
def create_proxy():
    TINSOFT_KEY = os.getenv('TINSOFT_KEY')
    url = f'https://proxy.tinsoftsv.com/api/changeProxy.php?key={TINSOFT_KEY}'
    response = requests.get(url)
    proxy = response.json()
    if proxy['success'] == True:
        with open('proxy.txt','w') as f:
            f.write(proxy['proxy'])
    else:
        time.sleep(proxy['next_change']+1)
        return create_proxy()
def create_driver(page):         
    options = uc.ChromeOptions()
    # tắt load ảnh
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    # tắt thông báo
    options.add_argument("--disable-notifications")
    # add proxy 116.99.117.216:56753 vào chrome
    with open('proxy.txt','r') as f:
        proxy = f.read()
    options.add_argument('--proxy-server='+proxy)
    driver = uc.Chrome(options=options,headless=False,version_main=117)
    # set size cho chrome
    driver.set_window_size(320, 360)
    # set vị trí cho chrome
    driver.set_window_position((page-1)//3*320, (page-1)%3*360)
    return driver
def getPage(driver,page):
    if page == 1 or page == 0:
        url = 'https://batdongsan.com.vn/nha-dat-ban?sortValue=1'
    else:
        url = f'https://batdongsan.com.vn/nha-dat-ban/p{page}?sortValue=1'
    driver.set_page_load_timeout(10)
    try:
        driver.get(url)
    except:
        return []
    time.sleep(30)
    driver.save_screenshot('batdongsan.png')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # lấy tất cả link trong trang
    links = soup.find_all('a', class_='js__product-link-for-product-id')
    links = ['https://batdongsan.com.vn'+link['href'] for link in links]
    return links

def getHTML(driver,url):
    if redisdb.check_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw') == True:
        driver.set_page_load_timeout(10)
        try:
            driver.get(url)
            driver.save_screenshot('batdongsan.png')
        except:
            redisdb.delete_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw')
            return None
        time.sleep(1)
        html = driver.page_source
        return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': 'batdongsan.com.vn', 'data': html}
    else:
        return None


def crawl_one_thread(page):
    
    driver = create_driver(page)
    
    links = getPage(driver,page)
    #logging(f'Found {len(links)} links in page {page}')
    for link in links:
        data = getHTML(driver,link)
        if data != None:
            mongodb.insert(data)
            logging(f'Crawled website: batdongsan.com.vn, Id: {data["id_crawl"]}, Link: {link}')
    driver.quit()
        
def process():
      create_proxy()
      threads = []
      for i in range(1, 11):
         threads.append(threading.Thread(target=crawl_one_thread, args=(i,)))
      for thread in threads:
         thread.start()
         time.sleep(5)
      for thread in threads:
          thread.join()
      mongodb.close()
          
process()

