import random
import json
from collections import defaultdict
import requests

import visen

VISUB_INFO = {
    "south": "Nam",
    "north": "Bắc",
    "east": "Đông",
    "west": "Tây",
    "northeast": "Đông Bắc",
    "northwest": "Tây Bắc",
    "southeast": "Đông Nam",
    "southwest": "Tây Nam",
    "oneSideOpen": "một mặt thoáng",
    "twoSideOpen": "hai mặt thoáng",
    "threeSideOpen": "ba mặt thoáng",
    "fourSideOpen": "bốn mặt thoáng",
    'privateProperty': 'nhà riêng',
    'townhouse': 'nhà liền kề',
    'condominium': 'chung cư',
    'miniApartment': 'chung cư mini',
    'semiDetachedVilla': 'biệt thự liền kề',
    'privateLand': 'đất bán đất nền',
    'projectLand': 'đất dự án, đất nền dự án, dự án',
    'shophouse': 'nhà phố thương mại, shop house',
    'resort': 'nhà nghỉ, khu nghỉ dưỡng, resort',
    'otherTypesOfProperty': 'bất động sản khác'
}
class House:
    def __init__(self, property:dict, truncate_utility=3) -> None:
        """
        Class represent information of a house with input is a dict containing information
        
        Args
            property: dict containing information of a house with keys in self.data
        """
        self.property = property
        self.data = {
            "landSize": str (self.check(property, "landSize", None)) + " m2",
            "price": str(self.check(property, "price", None)).replace(".0", ""),
            "city": self.check(property, "city", None),
            "district": self.check(property, "district", None),
            "ward": self.check(property, "ward", None),
            "street": self.check(property, "street", None),
            "numberOfFloors": self.check(property, "numberOfFloors", None),
            "numberOfBathRooms": self.check(property, "numberOfBathRooms", None),
            "numberOfBedRooms": self.check(property, "numberOfBedRooms", None),
            "facade": str(self.check(property, "facade", None)) + "m",
            "houseDirection": self.check(property, "houseDirection", None),
            "facade": self.check(property, "facade", None),
            "typeOfRealEstate": self.check(property, "typeOfRealEstate", None),
        } 

        self.get_facilities()
        self.data["publicFacilities"] = self.check(self.property, "publicFacilities", None, truncate_utility)
        

    def get_facilities(self):
        address_types = ["street", "ward", "district", "city"]
        address = [self.property.get(a_type, "") for a_type in address_types]
        address = " ".join(address)
        slug = visen.remove_tone("-".join(address.lower().split()))
        params = {
            'slug': slug
        }
        response = requests.get('https://ailab.orai.io/extract_location_info/findpublicfacilities_v2.0.1', params=params)
        list_facilities = response.json()
        self.property["publicFacilities"] = list_facilities

    def check(self, object, key, default, truncate_utility=3):
        if key in object and object[key]:
            val = object[key]

            if type(val) != list and val in VISUB_INFO:
                val = VISUB_INFO[val]
            elif key == "publicFacilities":
                map_intro_facility = {
                    'restaurant': '\nNhà hàng gồm :',
                    'stadium': '\nSân vận động gồm :',
                    'clinic': '\nPhòng khám gồm :',
                    'parking': '\nBãi đậu xe gồm :',
                    'place_of_worship': '\nNơi thờ phụng gồm :',
                    'bus_stop': '\nĐiểm dừng xe buýt gồm :',
                    'kindergarten': '\nTrường mẫu giáo gồm :',
                    'marketplace': '\nChợ gồm :',
                    'atm': '\nTrạm rút tiền mặt tự động - ATM gồm :',
                    'supermarket': '\nSiêu thị gồm :',
                    'museum': '\nBảo tàng gồm :',
                    'school': '\nTrường học gồm :',
                    'university': '\nTrường đại học gồm :',
                    'college': '\nTrường cao đẳng gồm :',
                    'resort': '\nKhu nghỉ mát gồm :',
                    'dentist': '\nNha khoa gồm :',
                    'fuel': '\nTrạm xăng dầu - Nhiên liệu gồm :',
                    'embassy': '\nĐại sứ quán gồm :',
                    'aerodrome': '\nSân bay gồm :',
                    'townhall': '\nTòa thị chính gồm :',
                    'beach': '\nBãi biển gồm :',
                    'police': '\nAn ninh - Trụ sở công an gồm :',
                    'hospital': '\nBệnh viện gồm :',
                    'doctor': '\nBác sĩ gồm :',
                    'bay': '\nVịnh gồm :',
                    'water': '\nHồ xung quanh gồm :',
                    'park': '\nCông viên gồm :'
                } 
                grouped_data = defaultdict(list)
                except_val = ["Parking", "Atm", "Park", "Water", "Restaurant", "College",\
                               "Place_of_worship", "Dentist", "Kindergarten", "Marketplace",\
                                  "Fuel", "Total", "soccer", "Stadium", "Embassy", "Museum"]
                for item in val:
                    if item["name"] not in except_val:
                        name_item = f"\n- {item['name']}"
                        distance = round(item["distance"])
                        if distance < 1000:
                            distance = f"{distance}m"
                        else:
                            distance = f"{round(distance/1000, 1)}km"
                        name_item += f": {distance}"
                        if name_item not in grouped_data[item["type"]]:
                            grouped_data[item["type"]].append(name_item)
                facilities_str = ""
                for key in grouped_data:
                    if key in map_intro_facility:
                        grouped_data[key] = "".join(list(grouped_data[key])[:truncate_utility])
                        facilities_str += f"{map_intro_facility[key]}{grouped_data[key]}"
                return facilities_str

            if key == "price":
                if val >= 1000:
                    val = f"{val / 1000} tỷ"
                else:
                    val = f"{val} triệu"
            return val
        else:
            return default

    def __repr__(self) -> str:
        """Represent house's information as a string"""
        mapping_name = {
            'keyword': "địa chỉ",
            'price': "giá",
            'landSize': "diện tích",
            "typeOfRealEstate": "loại bất động sản:",
            'street' : "đường",
            "ward" : "phường",
            "district" : "quận",
            'city' : "thành phố",
            'phone': "liên lạc số điện thoại",
            'numberOfBedRooms': "phòng ngủ",
            'numberOfFloors': "tầng",
            'numberOfBathRooms': "phòng tắm",
            'road_width_in_front_of_house': "lối vào rộng",
            'interior': "nội thất",
            "houseDirection": "hướng",
            "facade": "mặt tiền",
            "publicFacilities": "Tiện ích xung quanh gồm:",
        }
        information = "Thông tin ngôi nhà này:"
        pre_keys = ['numberOfBedRooms', 'numberOfFloors','numberOfBathRooms']
        other_keys = list(set(mapping_name.keys()) - set(pre_keys))
        entities = [key for key in mapping_name if key in self.property]
        for key in entities:
            if key == "publicFacilities" and self.data.get(key):
                information += f"\n{mapping_name[key]}{self.data[key]}"
            elif key in pre_keys and "None" not in str(self.data[key]):
                information += f"\n- {self.data[key]} {mapping_name[key]},"
            elif key in other_keys and "None" not in str(self.data[key]):
                information += f"\n- {mapping_name[key]} {self.data[key]},"

        if information.endswith(","):
            information = information[:-1]
        return information

if __name__ == "__main__":

    with open("sample_house.json") as fi:
        house = json.load(fi)

    house_obj = House(property=house)
    print(str(house))