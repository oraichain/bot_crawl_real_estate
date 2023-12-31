import undetected_chromedriver as uc
import time
from bs4 import BeautifulSoup
import hashlib
import threading
from utils import logging, get_proxy, check_id_crawl, delete_id_crawl
from dotenv import load_dotenv
load_dotenv()
import os


#PROXY = get_proxy(2*60)

def save(id_crawl,data):
    with open(f'data/raw/batdongsan.com.vn/{id_crawl}','w') as f:
        f.write(data)
        
def create_driver(page):
    try:       
        options = uc.ChromeOptions()
        # tắt load ảnh
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument("--disable-notifications")
        #options.add_argument('--proxy-server='+PROXY)
        driver = uc.Chrome(options=options,headless=False,version_main=117)
        driver.set_window_size(320, 380)
        driver.set_window_position((page-1)//4*600, (page-1)%4*360)
        return driver
    except:
        return create_driver(page)


def getPage(driver,page):
    if page == 1 or page == 0:
        url = 'https://batdongsan.com.vn/nha-dat-ban-ha-noi?sortValue=1'
    else:
        url = f'https://batdongsan.com.vn/nha-dat-ban-ha-noi/p{page}?sortValue=1'
    driver.set_page_load_timeout(10)
    try:
        driver.get(url)
    except:
        return []
    time.sleep(3)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # lấy tất cả link trong trang
    links = soup.find_all('a', class_='js__product-link-for-product-id')
    links = ['https://batdongsan.com.vn'+link['href'] for link in links]
    return links


def getHTML(driver,url):
    if check_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw_s1') == True:
        try:
            driver.get(url)
        except:
            delete_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw_s1')
            return None
        time.sleep(1)
        html = driver.page_source
        return [hashlib.md5(url.encode()).hexdigest(),html]
    else:
        check_id_crawl(hashlib.md5(url.encode()).hexdigest(),'raw_s1')
        return None


def crawl_one_thread(page):
    print(f'Page: {page}')
    driver = create_driver(page)
    links = getPage(driver,page)
    for link in links:
        data = getHTML(driver,link)
        if data != None:
            save(data[0],data[1])
            logging(f'Crawled website: batdongsan.com.vn, Id: {hashlib.md5(link.encode()).hexdigest()}')
    driver.quit()
        
        
def run(i):
    threads = []
    for j in range(i,i+10,1):
        t = threading.Thread(target=crawl_one_thread, args=(j,))
        threads.append(t)
    for thread in threads:
        thread.start()
        time.sleep(1.5)
    for thread in threads:
        thread.join()
        
for h in range(1,300,10):
    run(h)
    

    
    

