
import re

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
    def extract_bedrooms(question):
        pattern = r"(\d+(?:[.,]\d+)?)\s*(?:phòng\s*)?ngủ"
        match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number_str = match.group(1).replace(',', '.')
            number = int(number_str)
            return number
        else:
            return None

    @staticmethod
    def extract_bathrooms(question):
        pattern = r"(\d+(?:[.,]\d+)?)\s*(?:phòng\s*|nhà\s*|)(vệ\s*sinh|tắm)"
        match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number_str = match.group(1).replace(',', '.')
            number = int(number_str)
            return number
        else:
            return None
        
    @staticmethod
    def extract_floors(question):
        pattern = r"(\d+(?:[.,]\d+)?)\s*(?:\s*)?tầng"
        match = re.search(pattern, question, flags=re.IGNORECASE)

        if match:
            number_str = match.group(1).replace(',', '.')
            number = int(number_str)
            return number
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
    def extract_price(string):
        min_val = ["từ", "thấp nhất", "bé nhất", "nhỏ nhất", "ít nhất", "rẻ nhất", "trên", "hơn", "trở lên", "đổ lên"]
        max_val = ["dưới", "không quá", "không vượt quá", "rẻ hơn", "nhỏ hơn", "bé hơn", "ít hơn", "thấp hơn", "cao nhất", \
                "đắt nhất", "lớn nhất", "nhiều nhất", "to nhất", "trở xuống", "đổ xuống", "đến", "tới", "-"]
        bound = "trên dưới|" + "|".join(max_val + min_val)
        pattern = f"(?:({bound})\s*)?(?:(khoang|la|khoảng|là)\s*)?(\d+(?:[.,]\d+)?)\s*(?:tỷ|triệu)\s*(?:(trở lên|đổ lên|trở xuống|đổ xuống))?(?!\s*/\s*m2)"
        match = re.search(pattern, string, flags=re.IGNORECASE)

        if match:
            context1 = match.group(1)
            price = float(match.group(3).replace(',', '.'))
            context2 = match.group(4)
            if "tỷ" in match.group():
                price *= 1000
                price = float(price)
        else:
            price = None

        if price == None:
            return None, None
        elif "trên dưới" in match.group():
            return "around", price
        elif context2 in max_val or context1 in max_val:
            return "less", price
        elif context2 in min_val or context1 in min_val:
            return "more", price
        else:
            return "around", price
    

        
        
    @staticmethod
    def extract_acreage(string):
        min_val = ["từ", "thấp nhất", "bé nhất", "nhỏ nhất", "ít nhất", "rẻ nhất", "trên", "hơn", "trở lên", "đổ lên"]
        max_val = ["dưới", "không quá", "không vượt quá", "rẻ hơn", "nhỏ hơn", "bé hơn", "ít hơn", "thấp hơn", "cao nhất", \
                "đắt nhất", "lớn nhất", "nhiều nhất", "to nhất", "trở xuống", "đổ xuống", "đến", "tới"]
        bound = "trên dưới|" + "|".join(max_val + min_val)
        pattern = f"(?:({bound})\s*)?(?:(khoang|la|khoảng|là)\s*)?(\d+(?:[.,]\d+)?)\s*(?:m2)\s*(?:(trở lên|đổ lên|trở xuống|đổ xuống))?(?!\s*/\s*m2)"
        match = re.search(pattern, string, flags=re.IGNORECASE)

        if match:
            context1 = match.group(1)
            num = float(match.group(3).replace(',', '.'))
            context2 = match.group(4)
        else:
            num = None

        if num == None:
            return None, None
        elif "trên dưới" in match.group():
            return "around", num
        elif context2 in max_val or context1 in max_val:
            return "less", num
        elif context2 in min_val or context1 in min_val:
            return "more", num
        else:
            return "around", num
    
    

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
        context, price = self.extract_price(question)
        if context == "around":
            entities["price"] = price
        elif context == "less":
            entities["maxPrice"] = price
            entities["price"] = price
        elif context == "more":
            entities["minPrice"] = price
            entities["price"] = price
        else:
            entities["price"] = None
        
        context, acreage = self.extract_acreage(question)
        if context == "around":
            entities["landSize"] = acreage
        elif context == "less":
            entities["maxLandSize"] = acreage
            entities["landSize"] = acreage
        elif context == "more":
            entities["minLandSize"] = acreage
            entities["landSize"] = acreage
        else:
            entities["landSize"] = None
        entities['facede'] = self.extract_facede(question)
        entities['number_of_floors'] = self.extract_floors(question)
        entities['number_of_toilets'] = self.extract_bathrooms(question)
        entities['number_of_bedrooms'] = self.extract_bedrooms(question)
        entities['price_per_acreage'] = self.extract_price_per_acreage(question)
        entities['road_width_in_front_of_house'] = self.extract_road_width_in_front_of_house(question)
        return entities

    def __call__(self, sentence):
        query = self.number_extractor(sentence)
        return query