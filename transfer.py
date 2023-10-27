import redis
import sys
from multiprocessing import Pool
sys.path.append('transfer')
import nhatot
import muaban
import batdongsan
import guland
import cafeland
import meeyland

sys.path.append('src')
from utils import logging, Duckdb
import json
import time
import threading
from dotenv import load_dotenv
from datetime import datetime
import os
load_dotenv()



redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
redisdb = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
duckdb = Duckdb()

def compare_set(set_name1,set_name2):
      set1 = redisdb.smembers(set_name1)
      set2 = redisdb.smembers(set_name2)
      set3 = set1.difference(set2)
      return set3




def etl_thread(datas):
    for data in datas:
        website_handlers = {
        'nhatot.com': nhatot.transferNhatot,
        'muaban.net': muaban.transferMuaban,
        'batdongsan.com.vn': batdongsan.transferBatdongsan,
        'guland.vn': guland.transferGuland,
        'cafeland.vn': cafeland.transferCafeland,
        'meeyland.com': meeyland.transferMeeyland,
        }
        
        website = data['website']
        if website in website_handlers:
                dataTransfer = website_handlers[website](data['data'])
                if dataTransfer is not None:
                    dataUpdate = [str(data['id_crawl']),str(dataTransfer)]
                    dataUpdate = ['600c9ced4cab5b80d6d0438980437fe3', "{'propertyType': 'houseForSale', 'propertyStatus': 'SURVEYING', 'mediaInfo': {'propertyGeneralImage': [{'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/2be52ce08058d5e72d0d2b96672477ceb0cbd43d731cf81f94b10fb6299679db.jpg', 'fileMimeType': 'image/png', 'isThumbnail': True}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/6f1ee75e4d64dd673b691dcc77569f25a3dfefbf88302971d289a6e6bf87e430.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/6ad23d0752f10d8ef8ce215372dffeee63a059abcb0bc5e804c917f69b6fe1bd.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/cc9ba8cf3b3a2265d28497d0e2240f05bfada567f891b7803b84796a2936a7bc.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/600bd3c88d545528acc4c8f703876d535d80b303a875ee2c09b104173371b634.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/9005d7113f193485f9607d901a85680eade0a9aaabde6092001f3ae14f0f225a.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/5e43f473aa619ccb519b43d5d197a5fb2bfe8588ce82313f9d6adb37f7bb588d.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/b922cb0113d24cb17fb32931b706e63d111966d7154ddce74804d1a2e53dd448.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}, {'comment': [], 'status': 'UNSELECTED', 'fileUrl': 'https://neststock-common-file.s3.ap-southeast-1.amazonaws.com/62faec33fabf4b018e385fbc05aa0bdf5c6aab750e9ff05741c9ae584b85a895.jpg', 'fileMimeType': 'image/png', 'isThumbnail': False}], 'houseTourVideo': [], 'certificateOfLandUseRight': {'certificateStatus': 'yes', 'media': []}, 'constructionPermit': {'certificateStatus': 'no', 'media': []}}, 'houseInfo': {'value': {'numberOfFloors': 1, 'numberOfBedRooms': 4, 'numberOfBathRooms': 0, 'numberOfKitchens': 0, 'numberOfLivingRooms': 0, 'numberOfGarages': 0}, 'status': 'UNSELECTED', 'comment': []}, 'propertyBasicInfo': {'landType': {'comment': [], 'status': 'UNSELECTED', 'value': 'residentialLand'}, 'accessibility': {'comment': [], 'status': 'UNSELECTED', 'value': 'deepInTheAlley'}, 'distanceToNearestRoad': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'frontRoadWidth': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'address': {'comment': [], 'status': 'UNSELECTED', 'value': {'addressDetails': None, 'street': 'Chùa Láng', 'ward': 'Láng Thượng', 'district': 'Đống Đa', 'city': 'Hà Nội', 'country': 'Việt Nam'}}, 'description': {'comment': [], 'status': 'UNSELECTED', 'value': '+ Chính chủ cần bán nhà phố Chùa Láng, Đống Đa, khu vự an ninh, dân trí.+ Cực hiếm, vị trí quá đẹp, ngõ rộng ô tô đỗ cổng, 3 bước ra đường ô tô tránh.+ Nơi tập trung nhiều các trường Đại học lớn như Luật Hà Nội, Hành chính Quốc Gia, Ngoại Thương...+ Nhà dân tự xây khung cột BT cực chắc chắn, còn mới, đẹp ở ngay.+ View hồ rộng thoáng. Trước nhà có sân để xe. Có cây xanh mát mẻ.+ Thông tin chính xác, ảnh thật 100%.+ Liên hệ Mr Thăng 0978012955. Miễn trung gian.'}, 'geolocation': {'comment': [], 'status': 'UNSELECTED', 'value': {'latitude': {'comment': [], 'status': 'UNSELECTED', 'value': '21.023569'}, 'longitude': {'comment': [], 'status': 'UNSELECTED', 'value': '105.805173'}}}, 'typeOfRealEstate': {'comment': [], 'status': 'UNSELECTED', 'value': 'privateProperty'}, 'frontWidth': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'endWidth': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'facade': {'comment': [], 'status': 'UNSELECTED', 'value': 'oneSideOpen'}, 'houseDirection': {'comment': [], 'status': 'UNSELECTED', 'value': None}, 'landSize': {'comment': [], 'status': 'UNSELECTED', 'value': None}, 'contact': {'name': {'comment': [], 'status': 'UNSELECTED', 'value': 'Mr Thăng'}, 'role': 'houseOwner', 'phoneNumber': {'comment': [], 'status': 'UNSELECTED', 'value': '0978012955'}, 'avatarUrl': {'comment': [], 'status': 'UNSELECTED', 'value': ' '}}, 'price': {'comment': [], 'status': 'UNSELECTED', 'value': 5.9}, 'unitPrice': {'comment': [], 'status': 'UNSELECTED', 'value': 'billion'}, 'yearOfConstruction': {'comment': [], 'status': 'UNSELECTED', 'value': None}, 'saleHistory': {'time': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'price': {'comment': [], 'status': 'UNSELECTED', 'value': 0}}, 'amenities': {'comment': [], 'status': 'UNSELECTED', 'value': {'amenityStatus': False, 'bathRoom': [], 'bedRoomAndLaundry': [], 'kitchenAndDining': [], 'others': []}}, 'peopleCulturalStandard': {'comment': [], 'status': 'UNSELECTED', 'value': 'high'}, 'publicFacilities': {'comment': [], 'status': 'UNSELECTED', 'value': []}, 'downside': {'comment': [], 'status': 'UNSELECTED', 'value': []}}, 'saleInfo': {'potentialAnalysis': {'marketPrice': {'comment': [], 'status': 'UNSELECTED', 'value': 5000000000}, 'expensesForRenovationOrExpansion': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'estimatedProfit': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'threeYearFuturePricePotential': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'fiveYearFuturePricePotential': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'cashFlow': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'monthlyCashFlow': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'financialLeverage': {'comment': [], 'status': 'UNSELECTED', 'value': 0}, 'liquidity': {'comment': [], 'status': 'UNSELECTED', 'value': 'high'}}}, 'crawlInfo': {'id': '64572564', 'source': 's2', 'time': '2022-06-29T00:00:52'}}"]
                    duckdb.insert_post_neststock('post_neststock',dataUpdate)
                    redisdb.sadd('post_neststock', data['id_crawl'])
                    logging(f'Đã chuyển dữ liệu từ {website} sang neststock thành công')
                else:
                    redisdb.sadd('post_neststock_reject', data['id_crawl'])
        else:
                redisdb.sadd('post_neststock_reject', data['id_crawl'])
                logging(f'Reject ID: {data["id_crawl"]} - Website: {website}',level='error')

            
     
            

                  
     
            
                        
for vclvcl in range(1):
    id_crawl_no_reject = compare_set('raw','post_neststock_reject')
    id_crawl = compare_set('raw','post_neststock')
    list_id_crawl = id_crawl_no_reject.intersection(id_crawl)
    logging(f'Số lượng bài viết cần chuyển: {len(list_id_crawl)}')
        
    list_id_crawl = list(list_id_crawl)

    if len(list_id_crawl) > 5000:
        list_id_crawl = list_id_crawl[:5000]

    list_id_crawl = ', '.join([f"'{id_crawl}'" for id_crawl in list_id_crawl])
    datas = duckdb.select_many('raw',list_id_crawl)
    datas = [{'id_crawl':data[0],'website':data[1],'data':data[2]} for data in datas]
    
    #map = Pool(1)
    #map.map(etl_thread,datas)
    #map.close()
    #map.join()
    # chia nhỏ datas thành các 50 sublist
    
    if len(datas) < 100:
        step = 1
    else:
        step = len(datas)//100
    data_sublist = [datas[i:i+step] for i in range(0,len(datas),step)]
    threads = []
    for data in data_sublist:
        thread = threading.Thread(target=etl_thread,args=(data,))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    duckdb.close()
    
      
