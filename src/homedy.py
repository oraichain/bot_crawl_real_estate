
import requests
from bs4 import BeautifulSoup
from utils import logging, check_id_crawl, Duckdb
import hashlib

duckdb = Duckdb()

def getPage(page):
  url = f"https://homedy.com/ban-nha-dat-ha-noi/p{page}?sort=new"
  payload={}
  headers = {
    'authority': 'mogi.vn',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
    'cache-control': 'max-age=0',
    'cookie': 'UID=57be77aa-23bc-49c3-ad09-de54ade7bc5d; _gcl_au=1.1.983895898.1690368610; _gid=GA1.2.1359403376.1690368611; _fbp=fb.1.1690368610702.808058211; __zi=3000.SSZzejyD5T4iWxwxraONXJBDiAEL6WMFBT_oiOCBGD1htlNrnWj4tMVRlV3510ZQOzMv_yC62TO.1; _ga_EPTMT9HK3X=GS1.1.1690447615.4.1.1690447943.59.0.0; _dc_gtm_UA-52097568-1=1; __gads=ID=734a7f4e446b8108-22bff834b6e70091:T=1690368626:RT=1690447943:S=ALNI_MbynPuvDSHnIXCGsm0XtXifQExdfA; __gpi=UID=000009f9421bf32a:T=1690368626:RT=1690447943:S=ALNI_MYdTCIV8_tAjNrDWaQDZ79WJLFX2Q; _ga=GA1.2.1301645986.1690368611; _gat_UA-52097568-1=1',
    'sec-ch-ua': '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  soup = BeautifulSoup(response.text, 'html.parser')
  links = soup.find_all('a', class_='title padding-hoz')
  links = [f'https://homedy.com{link["href"]}' for link in links]
  return links
   
   
def getHTML(url):
  payload={}
  headers = {
  'authority': 'homedy.com',
  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
  'cookie': '_source_utm=organic; _source_campaign=default; _source_referrer=google; _gid=GA1.2.754350581.1693218818; userId=fb0a923f-aa3e-40e8-8e24-e5b14a4077a8; UserIdHomedyShare=fb0a923f-aa3e-40e8-8e24-e5b14a4077a8; _fbp=fb.1.1693218819207.1964814849; __gads=ID=561c1723827dd09a-229213b328e3004e:T=1693218822:RT=1693218822:S=ALNI_MZy7NcFY0yTdxPYQxZAghUjBr1nxg; __gpi=UID=00000c351c1d3fa6:T=1693218822:RT=1693218822:S=ALNI_MZKmA7J8AJjsAVty9viT79t0KFXPw; _ga_3TM6MNV523=GS1.1.1693218818.1.1.1693218848.30.0.0; _ga=GA1.1.1023301757.1693218818; _ga_W67931SQGN=GS1.2.1693218818.1.1.1693218864.14.0.0; .AspNetCore.Antiforgery.qKMI6Lrj50Q=CfDJ8PyCrl482c5Pv2aBwHCe-CxJx2gD3ptNY18vGsQhOkVoLPUd58mjigXklS4sOgpk1nBQhc9iwtflniSY4-GE5b_KJ3ezm-g12ma5kOFHJmX_IjaghPAQvyqDsGXGhQG-YmDcdir22GDAjpht9XpfJKk',
  'referer': 'https://homedy.com/ban-nha-dat/p7',
  'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'document',
  'sec-fetch-mode': 'navigate',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-user': '?1',
  'upgrade-insecure-requests': '1',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  website = url.split("/")[2]
  return [hashlib.sha256(url.encode()).hexdigest(), website, response.text]


def run(offset):
  for i in range(1,offset):
    links = getPage(i)
    for link in links:
        if check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
          data = getHTML(link)
          duckdb.insert_raw('raw',data)
          logging(f'Crawled website: homedy.com, Id: {hashlib.md5(link.encode()).hexdigest()}')  
  duckdb.close()
  
run(2)