import datetime
from noti_logging import logging
import json
import re
import s3
with open('./transfer/streets.json', 'r') as f:
   streets = json.load(f)
def search_street(location):
   for street in streets:
      if street['STREET'].lower() in location and street['DISTRICT'].lower() in location:
         if street['WARD'].lower() in location:
            return street
   
   return None

def searchFloor(a):
   bio = a['content'].lower()
   if 'tầng' in bio:
      # tìm chữ số đứng trước chữ tầng
      floor = re.findall(r'\d+(?= tầng)', bio)
      if len(floor) > 0:
         return int(floor[0])
      else:
         bio = a['title'].lower()
         if 'tầng' in bio:
            # tìm chữ số đứng trước chữ tầng
            floor = re.findall(r'\d+(?= tầng)', bio)
            if len(floor) > 0:
               return int(floor[0])
   return 1
   
def certificateOfLandUseRight(a):
   return { "certificateStatus": "yes", "media": [] }
         
def time(a):
   date = a['publishedDate']
   # str = '2021-05-20T00:00:00.000Z' convert to '2021-05-20T00:00:00'
   date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')
   return date.strftime('%Y-%m-%dT%H:%M:%S')

def propertyType(a):
   return 'houseForSale'
   
def propertyGeneralImage(a):
   data = []
   if 'images' not in a:
      return None
   images = a['images']
   images = [s3.upload_image_to_s3(image['url']) for image in images]
   for image in images:
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

def houseInfo(a):
   value = {   "numberOfFloors": searchFloor(a),
               "numberOfBedRooms": 0,
               "numberOfBathRooms": 0,
               "numberOfKitchens": 0,
               "numberOfLivingRooms": 0,
               "numberOfGarages": 0 }
   if 'bedroom' in a:
      if a['bedroom'] != None:
         value['numberOfBedRooms'] = a['bedroom']
   if 'bathroom' in a:
      if a['bathroom'] != None:
         value['numberOfBathRooms'] = a['bathroom']
   return value

def propertyBasicInfo(a):
   return 'residentialLand'
   
def accessibility(a):
   if 'wideRoad' in a:
      if a['wideRoad'] != None:
         wideRoad = a['wideRoad']
         if 'Ngõ ngách' in wideRoad:
            return 'theBottleNeckPoint'
         if 'Ngõ 1 ô tô' in wideRoad:
            return 'fitOneCarAndOneMotorbike'
         if 'Ngõ 2 ô tô' in wideRoad:
            return 'fitTwoCars'
         if 'Ngõ 3 ô tô' in wideRoad:
            return 'fitThreeCars'
         if 'Ngõ 4 ô tô' in wideRoad:
            return 'notInTheAlley'
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
   if 'locations' in a:
      if 'streetName' in a['locations'][0]:
         if a['locations'][0]['streetName'] != None:
            fullAddress = a['locations'][0]['streetName'] + ' ' + a['locations'][0]['districtName'] + ' ' + a['locations'][0]['cityName']
            fullAddress = fullAddress.lower()
            search = search_street(fullAddress)
            if search != None:
               data['street'] = search['STREET']
               data['ward'] = search['WARD']
               data['district'] = search['DISTRICT']
               data['city'] = search['CITY']
               lat = search['LAT']
               lng = search['LNG']
               return [data,lat,lng]
   return None

def typeOfRealEstate(a):
  if 'typeOfHouse' in a:
     typeOfHouse = a['typeOfHouse'][0].lower()
     if 'căn hộ' in typeOfHouse:
        return 'condominium'
     if 'liền kề' in typeOfHouse or 'shophouse' in typeOfHouse:
        return 'shophouse'
     if 'biệt thự' in typeOfHouse:
        return 'semiDetachedVilla'
     if 'đất' in typeOfHouse:
        return 'privateLand'
     if 'khác' in typeOfHouse:
        return 'otherTypesOfProperty'
  return 'privateProperty'
   
def frontWidth(a):
   if 'facade' in a:
      if a['facade'] != None:
         frontwidth_ = a['facade']
         return float(frontwidth_)
   return 0

def facade(a):
      if '2 mặt' in a['content'].lower() or '2 mặt' in a['title'].lower():
         return 'twoSideOpen'
      elif '3 mặt' in a['content'].lower() or '3 mặt' in a['title'].lower():
         return 'threeSideOpen'
      elif '4 mặt' in a['content'].lower() or '4 mặt' in a['title'].lower():
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
   try:
      if 'direction' in a:
         direction = a['direction'][0]
         if direction == 'Đông':
            return 'east'
         elif direction == 'Tây':
            return 'west'
         elif direction == 'Nam':
            return 'south'
         elif direction == 'Bắc':
            return 'north'
         elif direction == 'Đông Nam':
            return 'southeast'
         elif direction == 'Đông Bắc':
            return 'northeast'
         elif direction == 'Tây Nam':
            return 'southwest'
         elif direction == 'Tây Bắc':
            return 'northwest'
      return None
   except:
      return None

def amenities(a):
   return True
 
def name(a):
   if 'creator' in a:
      if 'name' in a['creator']:
         name_ = a['creator']['name']['first'] + ' ' + a['creator']['name']['last']
         return name_.strip()
   return ''
 
def numberPhone(a):
   if 'creator' in a:
      if 'phone' in a['creator']:
         return a['creator']['phone']
   return ''

def avatarUrl(a):
   if 'creator' in a:
      if 'avatar' in a['creator']:
         if a['creator']['avatar'] != '':
            return a['creator']['avatar']
         else:
            return None
 
def landSize(a):
   if 'area' in a:
      if a['area'] != None:
         return a['area']
   return 0

def price(a):
   try:
      if 'priceLabel' in a:
         if 'lượng' in a['priceLabel']:
            return None
         price_ = a['priceLabel'].replace('Tỷ','').replace(',','.')
         return float(price_)
   except:
      return None

 
 

def transferMeeyland(a):
   price_ = price(a)
   if price_ == None:
      logging('meeyland.com: Không có giá')
      return None
   
   images_ = propertyGeneralImage(a)
   if images_ == None:
      logging('meeyland.com: Không có ảnh')
      return None
   # nếu data là houseForRent tạm thời bỏ qua
   propertyType_ = propertyType(a)
   if propertyType_ == 'houseForRent':
      logging('meeyland.com: Không phải bất động sản bán')
      return None
   # nếu address không có thì bỏ qua
   address_ = address(a)
   if address_ == None:
      logging('meeyland.com: Không có địa chỉ')
      return None
   
   # nếu houseDirection không có thì bỏ qua
   houseDirection_ = houseDirection(a)
   data_merge = {
               "propertyType": propertyType_,
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
                  "description": { "comment": [], "status": "UNSELECTED", "value": a['content'] },
                  "geolocation": { "comment": [], "status": "UNSELECTED", "value":{
                        "latitude": { "comment": [], "status": "UNSELECTED", "value": address_[1] },
                        "longitude": { "comment": [], "status": "UNSELECTED", "value": address_[2]}}},
                  "typeOfRealEstate": { "comment": [], "status": "UNSELECTED", "value": typeOfRealEstate(a) },
                  "frontWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "endWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "facade": { "comment": [], "status": "UNSELECTED", "value": facade(a) },
                  "houseDirection": { "comment": [], "status": "UNSELECTED", "value": houseDirection_ },
                  "landSize": { "comment": [], "status": "UNSELECTED", "value": landSize(a) },
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
               "crawlInfo": { "id": a['code'], "source" : 's10','time' : time(a)}}
      
   
   return data_merge


