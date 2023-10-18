import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import hashlib
import threading
import mongodb
from utils import logging, get_proxy
import redisdb
from dotenv import load_dotenv
load_dotenv()
mongodb = mongodb.MongoDB('tindangbatdongsan', 'raw')
PROXY = get_proxy(15*60)

def create_driver(page):         
    options = uc.ChromeOptions()
    # tắt load ảnh
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # fixed detection automation headless by cloudflare
    options.add_argument('--headless')
    options.add_argument('--disable-extensions')
    options.add_argument("--disable-notifications")
    options.add_argument('--proxy-server='+PROXY)
    driver = uc.Chrome(options=options,headless=False,version_main=117)
    driver.set_window_size(320, 360)
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
    driver.save_screenshot(f'./src/batdongsan.com.vn.png')
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # lấy tất cả link trong trang
    links = soup.find_all('a', class_='js__product-link-for-product-id')
    links = ['https://batdongsan.com.vn'+link['href'] for link in links]
    print(links)
    return links


def getHTML(driver,url):
    if redisdb.check_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw') == True:
        driver.set_page_load_timeout(10)
        try:
            driver.get(url)
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
    for link in links:
        data = getHTML(driver,link)
        if data != None:
            mongodb.insert(data)
            logging(f'Crawled website: batdongsan.com.vn, Id: {data["id_crawl"]}, Link: {link}')
    driver.quit()
        
        
def process():
      threads = []
      for i in range(1, 2):
         threads.append(threading.Thread(target=crawl_one_thread, args=(i,)))
      for thread in threads:
         thread.start()
         time.sleep(5)
      for thread in threads:
          thread.join()
      mongodb.close()
          
          
if __name__ == '__main__':          
    process()

