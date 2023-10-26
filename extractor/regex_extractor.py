
import re

import visen

from extractor.base_extractor import BaseExtractor


class RegexExtractor(BaseExtractor):
    
    def __init__(self, do_preprocess=False):
        super().__init__(do_preprocess)
    @staticmethod
    def extract_facede(question):
        pattern = r"mặt tiền.*?(\d+(?:[.,]\d+)?)\s*(?:m)"
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match is None:
            pattern = r"(\d+(?:[.,]\d+)?)\s*m(?![\d.])\s*mặt tiền"
            match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number = match.group(1).replace(',', '.')
            return float(number)
        else:
            return None

    @staticmethod
    def extract_range(string, value_type):
    
        value_patterns = {
            "price": {
                "unit": "tỷ|triệu",
                "multiplier": {"tỷ": 1000, "triệu": 1},
            },
            "landSize": {"unit": "m2"},
            "numberOfFloors": {"unit": "tầng|tang"},
            "numberOfBedRooms": {"unit": "phòng ngủ|ngủ|phong ngu|ngu"},
            "numberOfBathRooms": {"unit": "nhà vệ sinh|phòng vệ sinh|nhà tắm|\
tắm|tăm|tam|ve sinh|nha ve sinh|phong ve sinh|vệ sinh|phòng tắm|phong tam"}
        }
        value_pattern = value_patterns.get(value_type)
        unit = value_pattern["unit"]
        multiplier = value_pattern.get("multiplier", {})

        min_val = ["từ", "thấp nhất", "bé nhất", "nhỏ nhất", "ít nhất", "rẻ nhất", "trên", "hơn", "trở lên", "đổ lên"]
        max_val = ["dưới", "không quá", "không vượt quá", "rẻ hơn", "nhỏ hơn", "bé hơn", "ít hơn", "thấp hơn", "cao nhất", \
                "đắt nhất", "lớn nhất", "nhiều nhất", "to nhất", "trở xuống", "đổ xuống", "đến", "tới"]
        bound = "trên dưới|" + "|".join(min_val + max_val)
        pattern = f"({bound})?\s*(?:khoang|la|khoảng|là)?\s*( \d+(?:[.,]\d+)?)?\s*({unit})?\s*\
(đến|-|tới|lên đến|lên tới|den|toi|len den|len toi)?\s*(?:khoang|la|khoảng|là)?\s*(\d+(?:[.,]\d+)?)\s*({unit})\s*\
(trở lên|đổ lên|trở xuống|đổ xuống)?"
        match = re.search(pattern, string, flags=re.IGNORECASE)
        
        min_num = None
        max_num = None
        if match:
            second_num = float(match.group(5))
            second_unit = match.group(6)
            second_num *= multiplier.get(second_unit, 1)
            first_num = match.group(2)
            
            if first_num:
                first_unit = match.group(3)
                if not first_unit:
                    first_unit = second_unit
                first_num = float(first_num) * multiplier.get(first_unit, 1)
                min_num = min(first_num, second_num)
                max_num = max(first_num, second_num)
            else:
                prefix = match.group(1)
                suffix = match.group(7)
                if "tren duoi" in visen.remove_tone(match.group()):
                    max_num = second_num
                    min_num = second_num
                elif suffix in max_val or prefix in max_val:
                    max_num = second_num
                    min_num = None
                elif suffix in min_val or prefix in min_val:
                    max_num = None
                    min_num = second_num
                else:
                    max_num = second_num
                    min_num = second_num

        return min_num, max_num

    @staticmethod
    def extract_road_width_in_front_of_house(question):
        pattern = r"(?:đường trước nhà|lối vào|đường vào).*?(\d+(?:[.,]\d+)?)\s*(?:m)"
        match = re.search(pattern, question, flags=re.IGNORECASE)
        if match is None:
            pattern = r"(\d+(?:[.,]\d+)?)\s*m(?![\d.])\s*(?:đường trước nhà|lối vào|đường vào)"
            match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number = match.group(1).replace(',', '.')
            return float(number)
        else:
            return None  

    @staticmethod
    def extract_price_per_acreage(question):

        pattern = r"(\d+(?:[.,]\d+)?)\s*(?:triệu|tỷ)\s*(?:/|1|một|)\s*m2"
        match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number_str = match.group(1).replace(',', '.')
            number = float(number_str)
            if 'tỷ' in match.group():
                number *= 1000
            return number
        else:
            return None
    @staticmethod
    def extract_m(string):
        try:
            match = re.match(r'^(\d+(\.\d+)?)\s*m$', string)
            num = float(match.group(1))
            return num
        except:
            return None

    def number_extractor(self, question):
        if self.do_preprocess:
            question = self.preprocess_text(question)
        entities = {}
        for entity_type in ["price", "landSize", "numberOfBedRooms", "numberOfBathRooms", "numberOfFloors"]:
            min_num, max_num = self.extract_range(question, entity_type)
            if min_num == max_num:
                entities[entity_type] = min_num
            else:
                entities[f"min{entity_type[0].upper()}{entity_type[1:]}"] = min_num
                entities[f"max{entity_type[0].upper()}{entity_type[1:]}"] = max_num    
        entities['facede'] = self.extract_facede(question)
        entities['road_width_in_front_of_house'] = self.extract_road_width_in_front_of_house(question)
        return entities

    def __call__(self, sentence):
        query = self.number_extractor(sentence)
        return query