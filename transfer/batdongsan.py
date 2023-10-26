from bs4 import BeautifulSoup
from noti_logging import logging
import json
import datetime
from unidecode import unidecode
import re
import time
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




# Các hàm chuyên của batdongsan.com.vn
def text_to_slug(text):
   return unidecode(text).replace(' ', '_').lower()
def details_batdongsan(a):
   soup = BeautifulSoup(a, 'html.parser')
   details_ = soup.find_all('div', class_='re__pr-specs-content-item')
   details_ = [item.text.strip() for item in details_]
   json_ = {}
   for item in details_:
      key, value = item.split('\n')
      json_[text_to_slug(key)] = value
   return json_

def propertyGeneralImage(a):
   data = []
   soup = BeautifulSoup(a, 'html.parser')
   link_image_ = soup.find_all('img', title=True, src=True)
   link_image_ = [item['src'] for item in link_image_]
   link_image_ = [item for item in link_image_ if 'https://file4.batdongsan.com.vn' in item]
   link_image_ = [s3.upload_image_to_s3(item) for item in link_image_]
   if len(link_image_) == 0:
      return None
   # từ link_image_ lấy ra link ảnh và xoá đi tham số từ resize đến hết / thứ 2
   for i in range(len(link_image_)):
      link_image_[i] = re.sub(r'resize/.*?/', '', link_image_[i])
   for image in link_image_:
      data.append({
                    "comment": [],
                    "status": "UNSELECTED",
                    "fileUrl": image,
                    "fileMimeType": "image/png"
                })
   if len(data) > 0:
      data[0]['isThumbnail'] = True
   # thêm trường isThumbnail = True vào image đầu
   return data

def certificateOfLandUseRight(a):
   details_ = details_batdongsan(a)
   if 'phap_ly' in details_:
      if 'đỏ' in details_['phap_ly'] or 'hồng' in details_['phap_ly']:
         return { "certificateStatus": "yes","media": [] }
   return { "certificateStatus": "no", "media": [] }

def houseInfo(a):
   value = {   "numberOfFloors": 1,
               "numberOfBedRooms": 0,
               "numberOfBathRooms": 0,
               "numberOfKitchens": 0,
               "numberOfLivingRooms": 0,
               "numberOfGarages": 0 }
   details_ = details_batdongsan(a)
   if 'so_tang' in details_:
      value['numberOfFloors'] = int(details_['so_tang'].replace(' tầng', ''))
   if 'so_phong_ngu' in details_:
      value['numberOfBedRooms'] = int(details_['so_phong_ngu'].replace(' phòng', ''))
   if 'so_toilet' in details_:
      value['numberOfBathRooms'] = int(details_['so_toilet'].replace(' phòng', ''))
   return value

def accessibility(a):
   street_in = details_batdongsan(a)
   if 'duong_vao' in street_in:
      street_meter = float(street_in['duong_vao'].replace('m', '').replace(',', '.'))
      if street_meter <= 3:
         return 'theBottleNeckPoint'
      elif street_meter > 3 and street_meter <= 5:
         return 'parkCar'
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
   address_ = soup.find('span', class_='re__pr-short-description js__pr-address')
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
         lng = address_search['LNG']
         return [data, lat, lng]
   else:
      data['street'] = address_search['STREET']
      data['ward'] = address_search['WARD']
      data['district'] = address_search['DISTRICT']
      data['city'] = address_search['CITY']
      lat = address_search['LAT']
      lng = address_search['LNG']
      return [data, lat, lng]


def description(a):
   soup = BeautifulSoup(a, 'html.parser')
   bio_ = soup.find('div', class_='re__section-body re__detail-content js__section-body js__pr-description js__tracking').text
   return bio_

def typeOfRealEstate(a):
   soup = BeautifulSoup(a, 'html.parser')
   property_ = soup.find('a', class_='re__link-se')
   property_ = property_['href']
   if 'ban-dat-nen' in property_:
      return 'projectLand'
   if 'ban-nha-rieng' in property_:
      return 'privateProperty'
   if 'ban-dat' in property_:
      return 'privateLand'
   if 'ban-nha-biet-thu-lien-ke' in property_:
      return 'townhouse'
   if 'ban-nha-mat-pho' in property_:
      return 'semiDetachedVilla'
   if 'trang-trai' in property_:
      return 'resort'
   if 'ban-shophouse' in property_:
      return 'shophouse'
   else:
      return 'otherTypesOfProperty'
   
def frontWidth(a):
   details_ = details_batdongsan(a)
   if 'mat_tien' in details_:
      return float(details_['mat_tien'].replace('m', '').replace(',', '.'))
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
   details_ = details_batdongsan(a)
   if 'huong_nha' in details_:
      if 'Tây - Bắc' in details_['huong_nha']:
         return 'northwest'
      elif 'Tây - Nam' in details_['huong_nha']:
         return 'southwest'
      elif 'Đông - Nam' in details_['huong_nha']:
         return 'southeast'
      elif 'Đông - Bắc' in details_['huong_nha']:
         return 'northeast'
      elif 'Tây' in details_['huong_nha']:
         return 'west'
      elif 'Đông' in details_['huong_nha']:
         return 'east'
      elif 'Nam' in details_['huong_nha']:
         return 'south'
      elif 'Bắc' in details_['huong_nha']:
         return 'north'
      else:
         return None
   else:
      return None

def landSize(a):
   details_ = details_batdongsan(a)
   if 'dien_tich' in details_:
      try:
         return float(details_['dien_tich'].replace('m²', '').replace('.', '').replace(',', '.'))
      except:
         return None
      
def name(a):
   soup = BeautifulSoup(a, 'html.parser')
   name_ = soup.find('div', class_='re__contact-name js_contact-name')
   if name_ == None:
      return None
   else:
      name_ = name_.text.strip()
   return name_
      
def numberPhone(a):
   soup = BeautifulSoup(a, 'html.parser')
   phone = soup.find('div', class_='re__btn re__btn-cyan-solid--md phone js__phone phoneEvent js__phone-event')
   if phone == None:
      return None
   phone = phone.text.strip()
   phone = phone.replace(' ', '')
   phone = phone.replace('·Hiệnsố', '')
   return phone 
      
def avatarUrl(a):
   soup = BeautifulSoup(a, 'html.parser')
   avatar = soup.find('img', class_='re__contact-avatar')
   if avatar == None:
      return None
   else:
      return avatar['src']
      
def price(a):
   try:
      soup = BeautifulSoup(a, 'html.parser')
      price_ = soup.find('div', class_='re__pr-short-info-item js__pr-short-info-item')
      price_ = price_.find('span', class_='value').text.strip()
      if 'tỷ' in price_:
         price_ = float(price_.replace(' tỷ', '').replace(',', '.'))
      elif 'triệu' in price_:
         price_ = float(price_.replace(' triệu', '').replace(',', '.'))/1000
      return float(price_)
   except:
      return None  
      
def amenities(a):
   details_ = details_batdongsan(a)
   if 'noi_that' in details_:
      return True
   else:
      return False
      
def id(a):
   soup = BeautifulSoup(a, 'html.parser')
   id_ = soup.find_all('div', class_='re__pr-short-info-item js__pr-config-item')
   for idz in id_:
      if 'Mã tin' in idz.text:
         return idz.text.replace('Mã tin', '').strip()
      
def time(a):
   soup = BeautifulSoup(a, 'html.parser')
   date = soup.find_all('div', class_='re__pr-short-info-item js__pr-config-item')
   date = [item.text.strip() for item in date]
   date = date[0].replace('Ngày đăng', '')
   date = datetime.datetime.strptime(date, '%d/%m/%Y')
   return date.strftime('%Y-%m-%dT%H:%M:%S')
   

      

   
   
def transferBatdongsan(a):
   images_ = propertyGeneralImage(a)
   if images_ == None:
      logging('batdongsan.com.vn: Không có ảnh')
      return None
   
   
   address_ = address(a)
   if address_ == None:
      logging('batdongsan.com.vn: Không có địa chỉ')
      return None
   
   
   houseDirection_ = houseDirection(a)
   
   
   price_ = price(a)
   if price_ == None:
      logging('batdongsan.com.vn: Không có giá')
      return None
   
   landSize_ = landSize(a)
   if landSize_ == None:
      logging('batdongsan.com.vn: Không có diện tích')
      return None
   
   
   data_merge = {
               "propertyType": 'houseForSale',
               "propertyStatus": "SURVEYING",
               "mediaInfo": { "propertyGeneralImage" : images_,
                              "houseTourVideo" : [], # chưa có video
                              "certificateOfLandUseRight": certificateOfLandUseRight(a),
                              "constructionPermit": { "certificateStatus": "no", "media": []  }},
               "houseInfo": { "value": houseInfo(a), "status": "UNSELECTED", "comment": [] },
               "propertyBasicInfo": { "landType": { "comment": [], "status": "UNSELECTED", "value": 'residentialLand' },
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
               "crawlInfo": { "id": id(a), "source" : 's1','time' : time(a)}}
      
   
   return data_merge