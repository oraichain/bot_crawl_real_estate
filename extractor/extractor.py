import requests
from thefuzz.fuzz import token_set_ratio

from extractor.ner_extractor import NERExtractor
from extractor.regex_extractor import RegexExtractor
from extractor.address_extractor import AddressExtractor
from utils.text_preprocessor import TextPreprocessor
class Extractor:

    def __init__(
        self,
        ner_path,
        url_ner,
        address_path="data/address/vn_address.json",
        do_preprocess=True
    ) -> None:
        self.ner_extractor = NERExtractor(ner_path, url_ner)
        self.regex_extractor = RegexExtractor()
        self.address_extractor = AddressExtractor(
            address_path=address_path
        )
        if do_preprocess:
            self.preprocess_text = TextPreprocessor()
            self.do_preprocess = True
        else:
            self.do_preprocess = False
    
    def post_process(self, entities, threshold_filter=80):
        
        sub_type_house = {
            "nhà riêng": "privateProperty",
            "nhà liền kề": "townhouse",
            "chung cư": "condominium",
            "chung cư mini": "miniApartment",
            "biệt thự liền kề": "semiDetachedVilla",
            "đất bán đất nền": "privateLand",
            "đất dự án, đất nền dự án, dự án": "projectLand",
            "nhà phố thương mại, shop house": "shophouse",
            "nhà nghỉ, khu nghỉ dưỡng, resort": "resort",
            "bất động sản khác": "otherTypesOfProperty"
        }
        if "type_of_house" in entities:
            key_types = list(sub_type_house.keys())[:-1]
            val = entities["type_of_house"]
                
            entities.pop("type_of_house")
            if val in sub_type_house:
                entities["typeOfRealEstate"] = sub_type_house[val]
            else:
                scores = list(map(lambda type: token_set_ratio(val, type), key_types))
                max_score = max(scores)
                if max_score > threshold_filter:
                    norm_type = key_types[scores.index(max_score)]
                    entities["typeOfRealEstate"] = sub_type_house[norm_type]

        entities = {
            key: value for key, value in entities.items() 
            if value is not None and value != ""
        }
        entities = {
            key: int(val) if str(val).strip().endswith('.0') else val
            for key, val in entities.items()
        }
        return entities

    # @staticmethod
    # def norm_text(text):
    #     try:
    #         response = requests.post(
    #             url="https://118.138.233.223:1521/Capu",
    #             json={"query": text},
    #             verify=False
    #         ).json()
    #         norm_text =  response["result"]["text"]
    #     except:
    #         norm_text = text
    #     return norm_text

    def __call__(self, text):
        if self.do_preprocess:
            text = self.preprocess_text(text)
        # text = self.norm_text(text)
        # Entities from NER model
        entities = self.ner_extractor(text)
        
        # Entities from Regex
        regex_entities = self.regex_extractor(text)
        for k, v in regex_entities.items():
            entities[k] = v
        
        # Entities from Address extractor
        if "address" in entities:
            address_entities = self.address_extractor(entities["address"])
            entities.update(address_entities)
        
        # Post process
        entities = self.post_process(entities)
        
        return entities