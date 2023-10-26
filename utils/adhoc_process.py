import re
import pandas as pd

def preprocess_price(price):
    """
    Preprocess a string containing a numerical value in billions or millions format.
    
    Args:
    price (str): input string containing a numerical value in the format "X billion" or "X million"
    
    Returns:
    float: the numerical value converted to a float, where "billion" is multiplied by 1000 and "million" is not
    """
    pattern = r'[-+]?\d*\.\d+|\d+'
    num = float(re.findall(pattern, price)[0])

    price = price.lower().strip() # convert to lowercase and remove whitespace
    if "tỷ" in price:
        return 1000 * num
    elif "triệu" in price:
        return num
    else:
        return 0


map_col = {
    "type_sale": "",
    'type_of_house': "",
    'address': "địa chỉ",
    'price': "giá",
    'acreage': "diện tích",
    'facede': "mặt tiền",
    'phone': "liên lạc số điện thoại",
    'number_of_bedrooms': "số phòng ngủ",
    'number_of_floors': "số tầng",
    'number_of_toilets': "số nhà vệ sinh",
    'road_width_in_front_of_house': "lối vào rộng",
    'the_direction_of_the_house': "nhà hướng",
    'interior': "nội thất",
}
def concat_rows_to_text(row: pd.Series, separator: str = " ") -> str:
    """
    Concatenates the values in each row of a pandas DataFrame into a single text string.
    
    Args:
        df (pd.DataFrame): The DataFrame to concatenate.
        separator (str, optional): The separator to use between values in each row. Defaults to " ".
    
    Returns:
        str: The concatenated text string.
    """
    texts = []
    features = list(map_col.keys())
    for feature in features:
        if type(row[feature]) == str:
            texts.append("{} {}".format(map_col[feature], row[feature]))
    print(texts)
    return " ".join(texts)


import re

def convert_m2(string):
    try:
        match = re.match(r'^(\d+(\.\d+)?)\s*m2$', string)
        num = float(match.group(1))
        return num
    except:
        return 0

def convert_m(string):
    try:
        match = re.match(r'^(\d+(\.\d+)?)\s*m$', string)
        num = float(match.group(1))
        return num
    except:
        return 0




db = pd.read_csv("")
col = db.columns.tolist()



col = [s for s in col if s.endswith('desc')]
feature_col = [feature.replace('_desc','') for feature in col]
def gen_desc(query):
    desc = []
    for feature in feature_col:
        if query[feature] != 'không rõ':
            value = query[f'{feature}_desc']
            if feature != 'address' and  feature != 'the_direction_of_the_house' and feature != 'public_utility':
                value = value.lower()
            value = value[0].upper() + value[1:]
            desc.append(value)
    return '. '.join(desc)



def parse_features(raw_features):
    features = raw_features.copy()
    features['price'] = features['raw_price']
    features['price_per_acreage'] = features['raw_price_per_acreage']
    features['acreage'] = features['raw_acreage']
    features['facede'] = features['raw_facede']
    
    bio_list = {
        'address_desc': f"""Căn nhà {features['short_id']} nằm ở {features['address']}.""",
        'type_of_house_desc': f"""Đây là {features['type_of_house'].lower()}.""",
        'acreage_desc': f"""Nhà này có diện tích {features['acreage']}.""",
        'juridical_desc': f"""Nhà có {features['juridical'].lower()} hợp lệ.""",
        'facede_desc': f"""Mặt tiền của nhà rộng {features['facede']}.""",
        'number_of_floors_desc': f"""Nhà gồm có {features['number_of_floors']} tầng.""",
        'number_of_bedrooms_desc': f"""Nhà gồm có {features['number_of_bedrooms']} phòng ngủ.""",
        'number_of_toilets_desc': f"""Nhà gồm có {features['number_of_toilets']} nhà vệ sinh.""",
        'interior_desc': f"""Nội thất {features['interior']}.""",
        'price_desc': f"""Nhà được định giá là {features['price']}, tương đương khoảng {features['price_per_acreage']}.""",
        'the_direction_of_the_house_desc': f"""Nhà có hướng {features['the_direction_of_the_house']}.""",
        'road_width_in_front_of_house_desc': f"""Đường trước nhà rộng {features['road_width_in_front_of_house']}.""",
        'public_utility_desc': f"""Nhà này gần {features['public_utility']}."""

    }
    desc = {}
    for k in bio_list:
        k = k.replace("_desc", "")
        if features[k] == 'không rõ':
            desc[f'{k}_desc'] = 'không rõ'
        else: 
            desc[f'{k}_desc'] = bio_list[f'{k}_desc']
    raw_features = raw_features.to_dict()
    raw_features.update(desc)    
    return raw_features

df = pd.DataFrame()
from tqdm import trange
update_db = []

for i in trange(len(df)):
    features = df.iloc[i]
    update_db.append(parse_features(features))



def hide_utility(house_desc):
    sentences = house_desc.split('. ')
    last_sentence = sentences[-1]
    if last_sentence.startswith('Nhà này gần'):
        sentences = sentences[:-1]
    return '. '.join(sentences)
