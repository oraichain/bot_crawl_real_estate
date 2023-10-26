import random

import pandas as pd
from utils.clean_text import preprocess_text

map_col = {
    "type_sale": "",
    'type_of_house': "",
    'address': "địa chỉ",
    'price': "giá",
    'acreage': "diện tích",
    'facede': "mặt tiền",
    # 'phone': "liên lạc số điện thoại",
    'number_of_bedrooms': "số phòng ngủ",
    'number_of_floors': "số tầng",
    'number_of_toilets': "số nhà vệ sinh",
    'road_width_in_front_of_house': "lối vào rộng",
    'the_direction_of_the_house': "nhà hướng",
    'interior': "nội thất",
}

def generate_entity(row: pd.Series, seperator: str=" "):

    texts = []
    features = list(map_col.keys())
    for feature in features:
        if type(row[feature]) == str:
            feature_value = row[feature]
            if feature != "address":
                feature_value = feature_value.lower()
            texts.append("{} {}".format(map_col[feature], feature_value))
    


    pass


def replace_missing_values(dictionary):
    
    for key, value in dictionary.items():
        if value is None or value == "" or pd.isna(value) or (isinstance(value, list) and len(value) == 0):
            dictionary[key] = "không rõ"
    return pd.Series(dictionary)


def mapping_features(row_features: pd.Series):
    outputs = row_features.copy()
    outputs['public_utility'] = eval(outputs["public_utility"])
    outputs["public_utility"] = ", ".join(outputs.loc["public_utility"])
    outputs = replace_missing_values(outputs)
    return outputs

def parse_features(features):
    
    new_bio = f"""Căn nhà nằm trên địa chỉ {features['address']}.
Đây là {features['type_of_house'].lower()} có diện tích {features['acreage']}.
Nhà có {features['juridical'].lower()} hợp lệ.
Mặt tiền của nhà rộng {features['facede']}.
Bên trong nhà là {features['number_of_floors']} tầng, {features['number_of_bedrooms']} phòng ngủ, {features['number_of_toilets']} nhà vệ sinh. Nội thất {features['interior']}.
Nhà được định giá là {features['price']}, tương đương khoảng {features['price/acreage']}.
Nhà hướng {features['the_direction_of_the_house']} và đường trước nhà rộng {features['road_width_in_front_of_house']}.
Nhà gần với {features['public_utility']}.
    """

    return new_bio

def generate_description(row):

    mapped_features = mapping_features(row)
    bio = parse_features(mapped_features)
    bio = bio.replace("\n", " ")
    return bio