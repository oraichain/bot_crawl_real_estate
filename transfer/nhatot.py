import datetime
from noti_logging import logging
import json
import s3
with open('./transfer/streets.json', 'r') as f:
   streets = json.load(f)
def search_street(location):
   for street in streets:
      if street['STREET'].lower() in location and street['DISTRICT'].lower() in location:
         if street['WARD'].lower() in location:
            return street
  
   return None
   




def certificateOfLandUseRight(a):
   for id in a['parameters']:
      if id['id'] == 'property_legal_document':
         if id['value'] == 'Đã có sổ':
            return { "certificateStatus": "yes","media": [] }
         else:
            return { "certificateStatus": "no", "media": [] }
   return { "certificateStatus": "no", "media": [] }
         
def time(a):
   date = datetime.datetime.fromtimestamp(int(a['ad']['list_time']/1000))
   return date.strftime('%Y-%m-%dT%H:%M:%S')
def propertyType(a):
   if a['ad']['type'] == 'u' or a['ad']['category'] == 1050:
      return 'houseForRent'
   elif a['ad']['type'] == 's':
      return 'houseForSale'
   
   
   
def propertyGeneralImage(a):
   data = []
   if 'images' not in a['ad']:
      return None
   images = a['ad']['images']
   images = [s3.upload_image_to_s3(image) for image in images]
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
   value = {   "numberOfFloors": 1,
               "numberOfBedRooms": 0,
               "numberOfBathRooms": 0,
               "numberOfKitchens": 0,
               "numberOfLivingRooms": 0,
               "numberOfGarages": 0 }
   for j in a['ad']:
      if 'floors' in j:
         value['numberOfFloors'] = a['ad']['floors']
      if 'rooms' in j:
         value['numberOfBedRooms'] = a['ad']['rooms']
      if 'toilets' in j:
         value['numberOfBathRooms'] = a['ad']['toilets']
   return value


def propertyBasicInfo(a):
   if 'land_type' in a['ad']:
      if a['ad']['land_type'] == 4:
         return 'ruralLand'
      elif a['ad']['land_type'] == 3:
         return 'industrialLand'
      else:
         return 'urbanResidentialLand'
   else:
      return 'urbanResidentialLand'
   
   
def accessibility(a):
   if 'pty_characteristics' in a['ad']:
      if 2 in a['ad']['pty_characteristics']:
         return 'fitOneCarAndOneMotorbike'
   if 'house_type' in a['ad']:
      if a['ad']['house_type'] == 3:
         return 'theBottleNeckPoint'
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
   try:
      data['addressDetails'] = a['ad']['street_number']
   except:
      data['addressDetails'] = None
   try:
      location_ = a['ad']['ward_name'] + ', ' + a['ad']['area_name'] + ', ' + a['ad']['region_name']
      location_ = location_.lower()
   except:
      return None
   address_ = search_street(location_)
   if address_ == None:
      return None
   data['street'] = address_['STREET']
   data['ward'] = address_['WARD']
   data['district'] = address_['DISTRICT']
   data['city'] = address_['CITY']
   return data


def typeOfRealEstate(a):
   if a['ad']['category'] == 1020:
      return 'privateProperty'
   elif a['ad']['category'] == 1040:
      return 'privateLand'
   elif a['ad']['category'] == 1010:
      return 'condominium'
   elif 'house_type' in a['ad']:
      if a['ad']['house_type'] == 1:
         return 'townhouse'
      elif a['ad']['house_type'] == 2:
         return 'semiDetachedVilla'
      elif a['ad']['house_type'] == 3:
         return 'privateProperty'
      elif a['ad']['house_type'] == 4:
         return 'shophouse'
   else:
      return 'otherTypesOfProperty'
   
   
def frontWidth(a):
   witdh = 0
   for i in a['parameters']:
      if i['id'] == 'width':
         witdh = i['value'].split(' ')[0]
         try:
            return float(witdh)
         except:
            return 0
   return witdh


def facade(a):
   if '2 mặt' in a['ad']['subject'].lower() or '2 mặt' in a['ad']['body'].lower():
      return 'twoSideOpen'
   elif '3 mặt' in a['ad']['subject'].lower() or '3 mặt' in a['ad']['body'].lower():
      return 'threeSideOpen'
   elif '4 mặt' in a['ad']['subject'].lower() or '4 mặt' in a['ad']['body'].lower():
      return 'fourSideOpen'
   elif typeOfRealEstate(a) == 'townhouse':
      return 'twoSideOpen'
   elif typeOfRealEstate(a) == 'semiDetachedVilla':
      return 'twoSideOpen'
   elif typeOfRealEstate(a) == 'shophouse':
      return 'twoSideOpen'
   else:
      return 'oneSideOpen'
   
def price(a):
   if 'price' in a['ad']:
      return a['ad']['price']/1000000000
   else:
      return None
   
def houseDirection(a):
   for i in a['parameters']:
      if i['id'] == 'direction':
         if i['value'] == 'Đông':
            return 'east'
         elif i['value'] == 'Tây':
            return 'west'
         elif i['value'] == 'Nam':
            return 'south'
         elif i['value'] == 'Bắc':
            return 'north'
         elif i['value'] == 'Đông Nam':
            return 'southeast'
         elif i['value'] == 'Đông Bắc':
            return 'northeast'
         elif i['value'] == 'Tây Nam':
            return 'southwest'
         elif i['value'] == 'Tây Bắc':
            return 'northwest'
   return None


def amenities(a):
   if 'furnishing_sell' in a['ad']:
      if a['ad']['furnishing_sell'] == 3 or a['ad']['furnishing_sell'] ==4:
         return False
      elif a['ad']['furnishing_sell'] == 1 or a['ad']['furnishing_sell'] == 2:
         return True
   else:
      return False
   
   
   

def transferNhatot(a):
   a = json.loads(a)
   images_ = propertyGeneralImage(a)
   if images_ == None:
      logging('nhatot.com: Không có ảnh')
      return None
   # nếu data là houseForRent tạm thời bỏ qua
   propertyType_ = propertyType(a)
   if propertyType_ == 'houseForRent':
      logging('nhatot.com: Không phải bất động sản bán')
      return None
   # nếu address không có thì bỏ qua
   address_ = address(a)
   if address_ == None:
      logging('nhatot.com: Không có địa chỉ')
      return None
   
   # nếu houseDirection không có thì bỏ qua
   houseDirection_ = houseDirection(a)
   if 'latitude' not in a['ad'] or 'longitude' not in a['ad']:
      logging('nhatot.com: Không có tọa độ')
      return None
   price_ = price(a)
   if price_ == None:
      logging('nhatot.com: Không có giá')
      return None
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
                  "address": { "comment": [], "status": "UNSELECTED", "value": address_ },
                  "description": { "comment": [], "status": "UNSELECTED", "value": a['ad']['body'] },
                  "geolocation": { "comment": [], "status": "UNSELECTED", "value":{
                        "latitude": { "comment": [], "status": "UNSELECTED", "value": a['ad']['latitude'] },
                        "longitude": { "comment": [], "status": "UNSELECTED", "value": a['ad']['longitude'] }}},
                  "typeOfRealEstate": { "comment": [], "status": "UNSELECTED", "value": typeOfRealEstate(a) },
                  "frontWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "endWidth": { "comment": [], "status": "UNSELECTED", "value": frontWidth(a) },
                  "facade": { "comment": [], "status": "UNSELECTED", "value": facade(a) },
                  "houseDirection": { "comment": [], "status": "UNSELECTED", "value": houseDirection_ },
                  "landSize": { "comment": [], "status": "UNSELECTED", "value": a['ad']['size'] },
                  "contact": { "name": { "comment": [], "status": "UNSELECTED", "value": a['ad']['account_name'] },
                     "role": "houseOwner",
                     "phoneNumber": { "comment": [], "status": "UNSELECTED", "value": a['ad']['phone'] },
                     "avatarUrl": { "comment": [], "status": "UNSELECTED", "value": a['ad']['avatar'] }},
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
               "crawlInfo": { "id": str(a['ad']['list_id']), "source" : 's4','time' : time(a)}}
      
   
   return data_merge