import requests
from bs4 import BeautifulSoup
from utils import logging, check_id_crawl, MongoDB
import hashlib


mongodb = MongoDB('tindangbatdongsan', 'raw')

def getPage(page):
   if page == 1 or page == 0:
      url = 'https://nhadat.cafeland.vn/nha-dat-ban-tai-ha-noi/'
   else:
      url = f"https://nhadat.cafeland.vn/nha-dat-ban-tai-ha-noi/page-{page}/"
   payload={}
   headers = {
   'authority': 'nhadat.cafeland.vn',
   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
   'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
   'cookie': 'locationCheckUser=1; _gid=GA1.2.2032050433.1693211067; _fbp=fb.1.1693211087973.1488392626; _gcl_au=1.1.743764431.1693211097; cf_clearance=ZZEz43ng63fbOVc8tmx8YV4M2iRYWb5DQnNn8YnGY.Q-1693220459-0-1-cb74a21f.49153cb8.9c75fdff-0.2.1693220459; __gads=ID=9b7cec377b164ef8:T=1693211067:RT=1693220459:S=ALNI_MaZofV0oScIsgSKzQXV_TY3zmg5EA; __gpi=UID=00000c35123d3438:T=1693211067:RT=1693220459:S=ALNI_MbRjZTDfYH0I8XoNnf6-meGuhiaqQ; _ga_LGJ40H0X06=GS1.1.1693220458.2.0.1693220459.59.0.0; cookieUrlSort=eyJpdiI6IjdOYWRKZExlY0ppcUVLcW1LYzVIRVE9PSIsInZhbHVlIjoicFNibnltQU5GS1dyUlh6RVVydk1wYjNSSVlHdDFjdkZIVk81Z21RamY1Q1I1UnVxU0JOeko1Zk9Nc2dVSVVNRyIsIm1hYyI6IjUzNzNlNjMyNTk1YWNkYTU5ZGNkMTJhZTI5MWJiMjEyNmQ1ZjBiYmQ4YjRmMDgwZGY5MjljODFlNDkwMWZiZWIifQ%3D%3D; cookieTypeSort=eyJpdiI6InRUdW14d3FZUTVNbklVaWZuaEJTYkE9PSIsInZhbHVlIjoib2tXM2R3RGp2bHhiNDBVeUdzUno0Zz09IiwibWFjIjoiNzFkZGMwNzc2YzgwZTE1ODIzZGI1NWFhYjc2MzdiYmNlZTEyODkyNWNhODY0YjU0ZmZmYWE2MjU0ZDYxNzI3NiJ9; giatriSearchUser=eyJpdiI6ImNDYllnWEZ2c1JzcjlcL2gzOU9OVWlnPT0iLCJ2YWx1ZSI6IjA1b2FUelRkK2p2XC9EaHhxVE1PUVhnPT0iLCJtYWMiOiI2NGZlMTZiYTY4MmI4NzhhZDgwZjFlNjIxZjk5ODg1ZTMwYjZiOTJkNzkwMTllZTllMDMxYTI4NDFiNWZjYTMzIn0%3D; _ga=GA1.1.1310822656.1693211067; _ga_D70VFMWRGM=GS1.1.1693220468.2.1.1693220651.57.0.0; XSRF-TOKEN=eyJpdiI6ImQzdDBQMWRLd0tJVzQ4MSsrM3JOTGc9PSIsInZhbHVlIjoiZ2Q2ZFVKbklzdzlkUDliU1lPMzZEUmJxWjNWU2krZjh3NDRRdElhUW9XeFBKK0xXRU54TnZDZ3lzSjZGYTcxZSIsIm1hYyI6Ijg3ODZiNTE3NjUzYTgwY2I3ZWE1YmM0OWI1MWQ3MzcyZmM3NWQ5NTRhYzI5YjQ4NTZjOTdkMmFlNjZiZTQ2OWEifQ%3D%3D; laravel_session=eyJpdiI6Ik1RM0IzVDI2c1YwUWMxN1JjSXlwS2c9PSIsInZhbHVlIjoidXcrOGFqeEZOMHRMYVwvMWpsbDQ2M1I2dVdrZUYzN3NRS1wvb1dtWXRja0VUWXM5R2swaldkKzhOSmU2SU9GNzlzIiwibWFjIjoiYWJmZmQ3ZTlhYTFjYzAxMTc1MDcyOWU4YmVhNjM4MDEzNTM2MmIyOTU2NjY5MWE3NTFjNGFhYmQ4M2FhZjdjZCJ9; XSRF-TOKEN=eyJpdiI6ImUxZTZrSzVYUWpKeGVhVmdFVGNoMEE9PSIsInZhbHVlIjoialdTU294MTVoM0haMXFaRWJkXC9ldzg1VjBIM2M3NEJOdzVMcnJoUG4wS1hQYWhpNEZFZERtWUlZRnRhVjgxdEUiLCJtYWMiOiI3OWFlNWI0NmNiZmQ0OWYwMTUxZDNhYTdkNjc5NTBmMWMwOGM2MWU0OTZjM2Y2YmI2ZjdlMWZkMmE2OTQ4Yjg0In0%3D; giatriSearchUser=eyJpdiI6IjF1RlhnZ2xiUGxxSXd6NnhzSW9Md1E9PSIsInZhbHVlIjoiUGFCajBvK2o3R1ZBSTdwK0pESUpFdz09IiwibWFjIjoiNmFlNzBjYTkxMTVjMGQzM2YyNjg4M2JmNjk5NDRjZWI2MDM1MWJjMzVhY2JhMTk0NDhhNmNhZjIzYzdkODFiMCJ9; laravel_session=eyJpdiI6ImRzSlp2S0NSXC9INldWSXB5RVVMdVFBPT0iLCJ2YWx1ZSI6ImxVN2Iwbm8raUxMUXlSSDhXaVBoR2NRZ3pMRERhK2RMb0MwdGRqXC9USFlzbmF5RXhLNWlqeVwvWnAybFNVU1FkSSIsIm1hYyI6ImFlODNhNzM4ZWFjYjY0NDI2MmMxMDczZDA1OWU1ZWY5MmNkYzgyNzIyNDVkMzVlN2Q2NGRmNTk5YWE3NDY3ZGYifQ%3D%3D',
   'referer': 'https://nhadat.cafeland.vn/nha-dat-ban/page-384/',
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

   soup = BeautifulSoup(response.text, 'html.parser')
   
   # tìm tất cả thẻ a chỉ có href và title nếu có thêm trường khác thì bỏ đi
   links = soup.find_all('a', attrs={'href': True, 'title': True})
   links = [link['href'] for link in links]
   # lọc link chỉ lấy link có dạng https://nhadat.cafeland.vn/... và có đuôi .html
   links = [link for link in links if link.startswith('https://nhadat.cafeland.vn/') and link.endswith('.html')]
   links = list(set(links))
   return links

def getHTML(url):

   payload={}
   headers = {
   'authority': 'nhadat.cafeland.vn',
   'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
   'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
   'cookie': 'locationCheckUser=1; _gid=GA1.2.2032050433.1693211067; _fbp=fb.1.1693211087973.1488392626; _gcl_au=1.1.743764431.1693211097; cf_clearance=ZZEz43ng63fbOVc8tmx8YV4M2iRYWb5DQnNn8YnGY.Q-1693220459-0-1-cb74a21f.49153cb8.9c75fdff-0.2.1693220459; __gads=ID=9b7cec377b164ef8:T=1693211067:RT=1693220459:S=ALNI_MaZofV0oScIsgSKzQXV_TY3zmg5EA; __gpi=UID=00000c35123d3438:T=1693211067:RT=1693220459:S=ALNI_MbRjZTDfYH0I8XoNnf6-meGuhiaqQ; _ga_LGJ40H0X06=GS1.1.1693220458.2.0.1693220459.59.0.0; cookieUrlSort=eyJpdiI6IjdOYWRKZExlY0ppcUVLcW1LYzVIRVE9PSIsInZhbHVlIjoicFNibnltQU5GS1dyUlh6RVVydk1wYjNSSVlHdDFjdkZIVk81Z21RamY1Q1I1UnVxU0JOeko1Zk9Nc2dVSVVNRyIsIm1hYyI6IjUzNzNlNjMyNTk1YWNkYTU5ZGNkMTJhZTI5MWJiMjEyNmQ1ZjBiYmQ4YjRmMDgwZGY5MjljODFlNDkwMWZiZWIifQ%3D%3D; cookieTypeSort=eyJpdiI6InRUdW14d3FZUTVNbklVaWZuaEJTYkE9PSIsInZhbHVlIjoib2tXM2R3RGp2bHhiNDBVeUdzUno0Zz09IiwibWFjIjoiNzFkZGMwNzc2YzgwZTE1ODIzZGI1NWFhYjc2MzdiYmNlZTEyODkyNWNhODY0YjU0ZmZmYWE2MjU0ZDYxNzI3NiJ9; giatriSearchUserCF=1-0-50-20048; giatriSearchUser=eyJpdiI6IkdaYlo3cjErR2dmd1JvS2dTc0lnUGc9PSIsInZhbHVlIjoieXVIRjFsYkpGM05wMWMwRUx5M2R0QT09IiwibWFjIjoiNWY4ZjY3Y2ZhOGEzMWVlYWZkOWM4NDI1MzA3MmYyYmYxMDNjNWE5NDk4YWQ5YjhmOGI3OGJkNjkwYmE2OTdkYyJ9; _ga=GA1.2.1310822656.1693211067; laravel_session=eyJpdiI6ImxPRkhURFpTaW5FTjNFREpVUVlMVWc9PSIsInZhbHVlIjoiNk9EdnJ2MlFsXC83Rk9LRUpQTHNyZ3VXcGFzbDBqemh5MVIzamt0XC9NU2JvQ2FVcXVYMEk1d0E1RlhZTEJ5YmZFIiwibWFjIjoiYmNkYTI4ZTdmMDVmOTJiNDAyMzg0ODZhNDMyNTRkNmFkYjJkN2FiNjhiZTQ3ZGE3OTdhMDE1M2QwOTg4NDQ3NiJ9; XSRF-TOKEN=eyJpdiI6ImpMYUs1NndFVEQ4aUxJNGxjYk1tMGc9PSIsInZhbHVlIjoidUFCT3AyZ0FPcGhjZnBhRXNETVFpQ2grWFZcL1hYWXd5cG8zWWkwbVNOeDRlN016ZlBvK0U4MWhxNWpQYVozYWUiLCJtYWMiOiI2NmFhMTc3YTdkOWQ2ODlmMDU3MDYxZGNjMDZjMTE4OWUyOWRlZjVkNDQ5YzI3YmQxZGEwYzJiZWViN2RiNjBjIn0%3D; chatcafeland_session=eyJpdiI6IllIR3NNVEphTGQ4MWNVODB5Q3M4c0E9PSIsInZhbHVlIjoiTWMwWWFhQkJ6QTJSTGlOWEs3dnU0OUpodzBUV2t1VWx2a21TNWVyT3h4RXdRcHdXRndZcElkXC9ISitrSXJzWU0iLCJtYWMiOiIyMGMxN2E4MGYzYWI4OTNhOGZhNDNhNzdiM2I2YTk0NjUyNjEyYmRlOWY2YzM4YTM1MDQ5NDkxMzlkNWE3ZTI3In0%3D; _ga_D70VFMWRGM=GS1.1.1693220468.2.1.1693221268.55.0.0; XSRF-TOKEN=eyJpdiI6InoyTGV0RE1NN3RmXC9KVTUxcm55eFZnPT0iLCJ2YWx1ZSI6InhxWnYreG9BUVBCNHNVbDY3dE52YXZoZU5kXC9qNFdwaVgwS1N5K3oyaDVOMWlMNFwvRzdGcU15YVNYT0FnXC93engiLCJtYWMiOiJkZjJlM2YyNDdlOWYzNjYzNDg5NTY0M2NlNWViYThmMzc1ZjBiNWI0MmFkYTZlZTM2ZmE1NGE0MmMwMTIwN2YzIn0%3D; giatriSearchUser=eyJpdiI6Im5DZlJSXC83Y2JtUWc5U203UERHZHhBPT0iLCJ2YWx1ZSI6Iml1S2YxeU1wWm5LdU1adTV6YTdoblE9PSIsIm1hYyI6ImRmYWU1OWQwZjlkYjg0OWEwOTM2N2RhN2Y2MzJkYzg1M2U0NzdlZGJjZDJkMDg3MThiMzBmMjMzMWM2NmJmNWQifQ%3D%3D; giatriSearchUserCF=2-8-63-135; laravel_session=eyJpdiI6IklPcjNTZnRVdGdSSUFhcTg5Zk9BUmc9PSIsInZhbHVlIjoiQ0xjZ2pQOEZTOVwvblk3TVNWM1M5S296SUkxU2J0WTdmTVV2aWU3NDZRSys4Rmx1dlNyQTJxaGxkNVNqdFwveDBcLyIsIm1hYyI6IjMwNTllZGNmYWRhN2Q0NzJkODUyMDYwYTU1ZDI3NGM4MDUyOTAwYjE2NzQzY2I0N2FiMGI5NThkNmM5OGQwMWQifQ%3D%3D',
   'referer': 'https://nhadat.cafeland.vn/nha-dat-ban/page-383/',
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
   website = 'cafeland.vn'
   return {'id_crawl': hashlib.md5(url.encode()).hexdigest(), 'website': website, 'data': response.text}
      
      
def run(offset):
   for i in range(1, offset):
      links = getPage(i)
      for link in links:
         if check_id_crawl(hashlib.md5(link.encode()).hexdigest(),'raw') == True:
            data = getHTML(link)
            mongodb.insert(data)
            logging(f'Crawled website: cafeland.vn, Id: {data["id_crawl"]}, Link: {link}')
   mongodb.close()


run(2)