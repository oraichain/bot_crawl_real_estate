
import json
from typing import Any
import requests


class GeoToolkit:

    def __init__(self) -> None:
        """
        This class use api get coordinate, and get publics utilities by this coordinate
        """
        self.coordinate_api = "http://api.positionstack.com/v1/forward?access_key=7c746d85f9afa6a7b61fb25e27cfb2f3&query="
        self.utilities_api = "https://api.orai.io/extract_location_info/findpublicfacilities"
    
    def get_coordinate(self, address):
        """
        Return coordinate given address text prior
        """
        url = self.coordinate_api + address
        response = requests.get(url=url)
        return json.loads(response.text)
    
    def get_utilities(self, lat, lon, dis):
        """
        Return utilities given coordinate
        """
        data = {
            "lat": lat,
            'lon': lon,
            'distance': dis
        }
        response = requests.get(
            url=self.utilities_api,
            params=data
        )
        return eval(response.text)
    

    @staticmethod
    def coordinate(address):
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=jsonv2&accept-language=vi&countrycodes=VN"

        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)
        return eval(response.text)

    def __call__(self, address, dis=1400) -> Any:
        try:
            coordinate = self.coordinate(address)[0]
            utilities = self.get_utilities(
                lat=coordinate['lat'],
                lon=coordinate['lon'],
                dis=dis
            )

            return utilities
        except:
            return []


if __name__ == '__main__':

    geo_tool = GeoToolkit()
    # Take facilities around "Thanh Xuân, Hà Nội"
    print(geo_tool("Thanh Xuân, Hà Nội"))
    # district = ['Thanh Trì', 'Gia Lâm',
    #    'Sóc Sơn', 'Hoài Đức', 'Đông Anh', 'Mê Linh', 'Ba Vì',
    #    'Thường Tín', 'Thạch Thất', 'Sơn Tây', 'Chương Mỹ', 'Thanh Oai',
    #    'Đan Phượng', 'Quốc Oai', 'Phúc Thọ', 'Mỹ Đức']

    # coordinates = [
    #     (20.934809, 105.839541),
    #     (21.024967, 105.964964),
    #     (21.276685, 105.835120),
    #     (21.029226, 105.700094),
    #     (21.165900, 105.851093),
    #     (21.182399, 105.708669),
    #     (21.124166, 105.382659),
    #     (20.848253, 105.884074),
    #     (21.026621, 105.539931),
    #     (21.119499, 105.472462),
    #     (20.886364, 105.670925),
    #     (20.858756, 105.787732),
    #     (21.112474, 105.679573),
    #     (20.968931, 105.608731),
    #     (21.102776, 105.547829),
    #     (20.671305, 105.721184)
    # ]
    # d_map = dict(zip(district, coordinates))
    # other = {
    #     'Ba Đình': (21.035398, 105.821821),
    #     'Bắc Từ Liêm': (21.075066, 105.760528),
    #     'Cầu Giấy': (21.036128, 105.795463),
    #     'Hai Bà Trưng': (21.008576, 105.859180),
    #     'Hoàn Kiếm': (21.030150, 105.854536),
    #     'Hoàng Mai': (20.978955, 105.864243),
    #     'Hà Đông': (20.961243, 105.761768),
    #     'Long Biên': (21.044808, 105.899197),
    #     'Nam Từ Liêm': (21.013235, 105.763298),
    #     'Thanh Xuân': (21.013235, 105.763298),
    #     'Tây Hồ': (21.066470, 105.825026),
    #     'Đống Đa': (21.015107, 105.827818)
    # }
    # d_map.update(other)


    # from utils.geo_toolkit import GeoToolkit
    # tool = GeoToolkit()
    # def adhoc(name, data):

    #     coordinate = {
    #         'latitude': data[0],
    #         'longitude': data[1],
    #         'distance': 2500
    #     }
    #     utilities = tool.get_utilities(coordinate=coordinate)
    #     utilities = [row for row in utilities if row['type'] != 'busStop']
    #     df_utilities = pd.DataFrame(utilities)
    #     df_utilities['district'] = name
    #     return df_utilities

    # all_ulti = []
    # for key in d_map:
    #     all_ulti.append(adhoc(key, d_map[key]))