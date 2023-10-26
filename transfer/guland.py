from bs4 import BeautifulSoup
from noti_logging import logging
import json
import datetime
from unidecode import unidecode
import re
import s3
with open('./transfer/streets.json', 'r') as f:
   streets = json.load(f)
def search_street(location):
   for street in streets:
      if street['STREET'].lower() in location and street['DISTRICT'].lower() in location:
         return street
   return None
with open('./transfer/projects.json', 'r') as f:
   projects = json.load(f)
def search_project(location):
   for project in projects:
      if project['PROJECT'].lower() in location and project['DISTRICT'].lower() in location:
         return project
   return None

# Các hàm chuyên của alohadat.com.vn
def text_to_slug(text):
   return unidecode(text).replace(' ', '_').lower()

def details_guland(a):
   soup = BeautifulSoup(a, 'html.parser')
   details_ = soup.find_all('div', class_='s-dtl-inf')
   metadata = {}
   for item in details_:
      key = item.find('div', class_='s-dtl-inf__lbl').text.strip()
      key = text_to_slug(key)
      value = item.find('div', class_='s-dtl-inf__val').text.strip()
      metadata[key] = value
   return metadata

def propertyType(a):
   # đang mặc định là bán nhà
   return 'houseForSale'

def propertyGeneralImage(a):
   data = []
   soup = BeautifulSoup(a, 'html.parser')
   link_image_ = soup.find_all('img', src=True)
   link_image_ = [item['src'] for item in link_image_ if item['src'].startswith('/files/') and item['src'].endswith('.jpg')]
   link_image_ = ['https://guland.vn' + item for item in link_image_]
   if len(link_image_) == 0:
      return None
   # từ link_image_ lấy ra link ảnh và xoá đi tham số từ resize đến hết / thứ 2
   for i in range(len(link_image_)):
      link_image_[i] = re.sub(r'resize/.*?/', '', link_image_[i])
   link_image_ = [s3.upload_image_to_s3(item) for item in link_image_]
   for image in link_image_:
      data.append({
                    "comment": [],
                    "status": "UNSELECTED",
                    "fileUrl": image,
                    "fileMimeType": "image/png",
                    "isThumbnail": False,
                })
   if len(data) > 0:
      data[0]['isThumbnail'] = True
   # thêm trường isThumbnail = True vào image đầu
   return data

def certificateOfLandUseRight(a):
   details_ = details_guland(a)
   if 'phap_ly:' in details_:
      if 'đỏ' in details_['phap_ly:'].lower() or 'hồng' in details_['phap_ly:'].lower():
         return { "certificateStatus": "yes","media": [] }
   return { "certificateStatus": "no","media": [] }
  
def houseInfo(a):
   value = {   "numberOfFloors": 1,
               "numberOfBedRooms": 0,
               "numberOfBathRooms": 0,
               "numberOfKitchens": 0,
               "numberOfLivingRooms": 0,
               "numberOfGarages": 0 }
   details_ = details_guland(a)
   if 'so_tang:' in details_:
      value['numberOfFloors'] = int(details_['so_tang:'])
   elif 'so_phong_ngu:' in details_:
      value['numberOfBedRooms'] = int(details_['so_phong_ngu:'])
   elif 'so_phong_tam:' in details_:
      value['numberOfBathRooms'] = int(details_['so_phong_tam:'])
   return value

def propertyBasicInfo(a):
   details_ = details_guland(a)
   if 'loai_bds:' in details_:
      propertyType_ = details_['loai_bds:'].lower()
      if 'căn hộ' in propertyType_ or 'nhà' in propertyType_ or 'thổ cư' in propertyType_:
         return 'residentialLand'
      elif 'nông' in propertyType_:
         return 'farmLand'
      elif 'công' in propertyType_:
         return 'industrialLand'
   return 'residentialLand'

def accessibility(a):
   street_in = details_guland(a)
   if 'duong/hem_vao_rong:' in street_in:
      street_meter = float(street_in['duong/hem_vao_rong:'].replace('m', '').replace(',', '.') )
      if street_meter <= 3:
         return 'theBottleNeckPoint'
      elif street_meter > 3 and street_meter <= 5:
         return 'fitOneCarAndOneMotorbike'
      elif street_meter > 5 and street_meter <= 7:
         return 'fitTwoCars'
      elif street_meter > 7 and street_meter <= 12:
         return 'fitThreeCars'
      else:
         return 'notInTheAlley'
   else:
      return 'notInTheAlley'

def address(a):
   data = {
   "addressDetails": '',
   "street": '',
   "ward": '',
   "district": '',
   "city": '',
   "country": "Việt Nam"
   }
   soup = BeautifulSoup(a, 'html.parser')
   address_ = soup.find('div', class_='dtl-stl__row')
   if address_ == None:
      return None
   address_ = address_.text.strip().lower()
   address_search = search_street(address_)
   if address_search == None:
      address_search = search_project(address_)
      if address_search == None:
         return None
      else:
         data = {
         'projectName': '',
         "district": '',
         "city": '',
         "country": "Việt Nam"
         }
         data['projectName'] = address_search['PROJECT']
         data['district'] = address_search['DISTRICT']
         data['city'] = address_search['CITY']
         lat = address_search['LAT']
         lon = address_search['LNG']
         return [data,lat,lon]
   else:
      data['street'] = address_search['STREET']
      data['ward'] = address_search['WARD']
      data['district'] = address_search['DISTRICT']
      data['city'] = address_search['CITY']
      lat = address_search['LAT']
      lon = address_search['LNG']
      return [data,lat,lon]

def description(a):
   soup = BeautifulSoup(a, 'html.parser')
   bio_ = soup.find('div', class_='dtl-inf__dsr')
   if bio_ == None:
      return ''
   return bio_.text

def typeOfRealEstate(a):
   details_ = details_guland(a)
   if 'loai_bds:' in details_:
      propertyType_ = details_['loai_bds:'].lower()
      if 'căn hộ' in propertyType_:
         return 'condominium'
      elif 'nhà phố' in propertyType_:
         return 'townhouse'
      elif 'biệt thự' in propertyType_:
         return 'semiDetachedVilla'
      elif 'liền kề' in propertyType_:
         return 'shophouse'
   return 'privateProperty'
   
def frontWidth(a):
   details_ = details_guland(a)
   if 'chieu_ngang:' in details_:
      return float(details_['chieu_ngang:'].replace('m', '').replace(',', '.'))
   else:
      return 0

def facade(a):
   bio_ = description(a)
   if '2 mặt' in bio_.lower():
      return 'twoSideOpen'
   elif '3 mặt' in bio_.lower():
      return 'threeSideOpen'
   elif '4 mặt' in bio_.lower():
      return 'fourSideOpen'
   elif typeOfRealEstate(a) == 'townhouse':
      return 'twoSideOpen'
   elif typeOfRealEstate(a) == 'semiDetachedVilla':
      return 'twoSideOpen'
   elif typeOfRealEstate(a) == 'shophouse':
      return 'twoSideOpen'
   else:
      return 'oneSideOpen'
   
def houseDirection(a):
   details_ = details_guland(a)
   if 'huong_cua_chinh:' in details_:
      if 'Tây Bắc' in details_['huong_cua_chinh:']:
         return 'northwest'
      elif 'Tây Nam' in details_['huong_cua_chinh:']:
         return 'southwest'
      elif 'Đông Nam' in details_['huong_cua_chinh:']:
         return 'southeast'
      elif 'Đông Bắc' in details_['huong_cua_chinh:']:
         return 'northeast'
      elif 'Tây' in details_['huong_cua_chinh:']:
         return 'west'
      elif 'Đông' in details_['huong_cua_chinh:']:
         return 'east'
      elif 'Nam' in details_['huong_cua_chinh:']:
         return 'south'
      elif 'Bắc' in details_['huong_cua_chinh:']:
         return 'north'
      else:
         return None
   else:
      return None

def landSize(a):
   soup = BeautifulSoup(a, 'html.parser')
   landSize_ = soup.find('div', class_='dtl-prc__sgl dtl-prc__dtc').text.strip()
   landSize_ = landSize_.replace('m²', '')
   if landSize_ == '':
      return 0
   return float(landSize_.replace('m²', ''))
   
def name(a):
   soup = BeautifulSoup(a, 'html.parser')
   name_ = soup.find('h5', class_='dtl-aut__tle').text.strip()
   return name_

def numberPhone(a):
   soup = BeautifulSoup(a, 'html.parser')
   phone = soup.find('a', class_='bnav-lnk bnav-lnk--call btn-call')['data-phone']
   return phone

def avatarUrl(a):
   soup = BeautifulSoup(a, 'html.parser')
   avatarUrl_ = soup.find('div', class_='dtl-aut__avt')
   avatarUrl_ = avatarUrl_.find('img', src=True)
   avatarUrl_ = avatarUrl_['src']
   if avatarUrl_ == '/bds_2/img/profile.png':
      return None
   else:
      return avatarUrl_
      
def price(a):
   try:
      soup = BeautifulSoup(a, 'html.parser')
      price_ = soup.find('div', class_='dtl-prc__sgl dtl-prc__ttl').text.strip()
      if 'tỷ' in price_:
         price_ = float(price_.replace(' tỷ', ''))
      elif 'triệu' in price_:
         price_ = float(price_.replace(' triệu', ''))/1000
      return float(price_)
   except:
      return None 
      
def amenities(a):
   bio_ = description(a).lower()
   if 'nội thất' in bio_:
      return True
   else:
      return False
   
def id(a):
   soup = BeautifulSoup(a, 'html.parser')
   id_ = soup.find('i', class_='mdi mdi-calendar-clock-outline').find_next('span').text.strip()
   return id_.replace('Mã tin: ', '')
  
def time(a):
   # lấy thời gian hiện tại
   date = datetime.datetime.now()
   return date.strftime('%Y-%m-%dT%H:%M:%S')    
   
def transferGuland(a):
   images_ = propertyGeneralImage(a)
   if images_ == None:
      logging('guland.vn: Không có ảnh')
      return None
   
   address_ = address(a)
   if address_ == None:
      logging('guland.vn: Không có địa chỉ')
      return None
   
   
   
   houseDirection_ = houseDirection(a)
   
   
   price_ = price(a)
   if price_ == None:
      logging('guland.vn: Không có giá')
      return None
   
   landSize_ = landSize(a)
   if landSize_ == None:
      logging('guland.vn: Không có diện tích')
      return None

   
   
   data_merge = {
               "propertyType": propertyType(a),
               "propertyStatus": "SURVEYING",
               "mediaInfo": { "propertyGeneralImage" : images_,
                              "houseTourVideo" : [], # chưa có video
                              "certificateOfLandUseRight": certificateOfLandUseRight(a),
                              "constructionPermit": { "certificateStatus": "no", "media": []  }},
               "houseInfo": { "value": houseInfo(a), "status": "UNSELECTED", "comment": [] },
               "propertyBasicInfo": { "landType": { "comment": [], "status": "UNSELECTED", "value": propertyBasicInfo(a) },
                  "accessibility": { "comment": [], "status": "UNSELECTED", "value": accessibility(a) },
                  "distanceToNearestRoad": { "comment": [], "status": "UNSELECTED", "value": 0 },
                  "frontRoadWidth": { "comment": [], "status": "UNSELECTED", "value": 0 },
                  "address": { "comment": [], "status": "UNSELECTED", "value": address_[0] },
                  "description": { "comment": [], "status": "UNSELECTED", "value": description(a) },
                  "geolocation": { "comment": [], "status": "UNSELECTED", "value":{
                        "latitude": { "comment": [], "status": "UNSELECTED", "value": address_[1] },
                        "longitude": { "comment": [], "status": "UNSELECTED", "value": address_[2] }}},
                  "typeOfRealEstate": { "comment": [], "status": "UNSELECTED", "value": typeOfRealEstate(a) },
                  "frontWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "endWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "facade": { "comment": [], "status": "UNSELECTED", "value": facade(a) },
                  "houseDirection": { "comment": [], "status": "UNSELECTED", "value": houseDirection_ },
                  "landSize": { "comment": [], "status": "UNSELECTED", "value": landSize_ },
                  "contact": { "name": { "comment": [], "status": "UNSELECTED", "value": name(a) },
                     "role": "houseOwner",
                     "phoneNumber": { "comment": [], "status": "UNSELECTED", "value": numberPhone(a) },
                     "avatarUrl": { "comment": [], "status": "UNSELECTED", "value": avatarUrl(a) }},
                  "price": { "comment": [], "status": "UNSELECTED", "value": price_ },
                  "unitPrice": { "comment": [], "status": "UNSELECTED", "value": "billion" },
                  "yearOfConstruction": { "comment": [], "status": "UNSELECTED", "value": None },
                  "saleHistory": { "time": { "comment": [], "status": "UNSELECTED", "value": 0 },
                     "price": { "comment": [], "status": "UNSELECTED", "value": 0 }},
                  "amenities": { "comment": [], "status": "UNSELECTED", "value": {
                        "amenityStatus": amenities(a), "bathRoom": [], "bedRoomAndLaundry": [], "kitchenAndDining": [], "others": [], }},
                  "peopleCulturalStandard": { "comment": [], "status": "UNSELECTED", "value": "high" },
                  "publicFacilities": { "comment": [], "status": "UNSELECTED", "value": [] },
                  "downside": { "comment": [], "status": "UNSELECTED", "value": [] }},
               "saleInfo": { "potentialAnalysis": { # ///
                     "marketPrice": { "comment": [], "status": "UNSELECTED", "value": 5000000000 },
                     "expensesForRenovationOrExpansion": { "comment": [],"status": "UNSELECTED","value": 0 },
                     "estimatedProfit": {"comment": [],"status": "UNSELECTED","value": 0 },
                     "threeYearFuturePricePotential": { "comment": [],"status": "UNSELECTED","value": 0 },
                     "fiveYearFuturePricePotential": {"comment": [],"status": "UNSELECTED","value": 0  },
                     "cashFlow": {"comment": [], "status": "UNSELECTED", "value": 0  },
                     "monthlyCashFlow": {"comment": [],"status": "UNSELECTED", "value": 0 },
                     "financialLeverage": {"comment": [],"status": "UNSELECTED","value": 0 },
                     "liquidity": { "comment": [],"status": "UNSELECTED","value": "high" }}},
               "crawlInfo": { "id": id(a), "source" : 's11','time' : time(a)}}
      
   
   return data_merge


