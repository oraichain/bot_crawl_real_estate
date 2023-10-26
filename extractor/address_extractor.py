import json
from typing import Any
import pandas as pd
import visen
import re
from difflib import SequenceMatcher

from extractor.es_extractor import ES

class AddressExtractor:

    def __init__(
        self,
        address_path="data/address/vn_address.json"
    ) -> None:
        with open(address_path, "r") as file:
            json_address = json.load(file)
        self.province = pd.DataFrame(json_address["province"])    
        self.district = pd.DataFrame(json_address["district"])    
        self.id2province = dict(zip(self.province['id'], self.province['province']))
       
        self.es = ES()

    @staticmethod
    def preprocess_text(text):
        text = text.lower()
        text = ''.join([c for c in text if c.isalnum() or c.isspace()])
        return text
    
    @staticmethod
    def get_bigrams(text):
        # Tokenize the preprocessed text into words
        tokens = text.split()
        bigrams = []
        for i in range(len(tokens) - 1):
            bigrams.append((tokens[i], tokens[i + 1]))
        # Generate bigrams
        return set(bigrams)
    
    def compare_texts(self, text1, text2):
        text1 = visen.remove_tone(text1)
        text2 = visen.remove_tone(text2)
        # Preprocess both texts
        text1 = self.preprocess_text(text1)
        text2 = self.preprocess_text(text2)

        # Get bigrams for both texts
        bigrams1 = self.get_bigrams(text1)
        bigrams2 = self.get_bigrams(text2)

        # Find common bigrams
        common_bigrams = bigrams1.intersection(bigrams2)

        num_word =len(text2.split())
        sim = 2 * len(common_bigrams) / num_word
        if sim > 1: 
            sim = 1
        return sim
    
    def score_address(self, raw_address, source_address, type_address, **kwargs):
        df = source_address.copy()
        if kwargs:
            id_type, id = list(kwargs.items())[0]
            df = df[df[id_type]==id].reset_index(drop=True)
        # df['score'] = df[type_address].apply(lambda text: fuzz.token_set_ratio(raw_address, text))
        df['score'] = df[type_address].apply(lambda text: self.compare_texts(raw_address, text))
        if 'weight' in df.columns and max(df['score']) > 0:
            df['score'] = df['score'] * df['weight']
        
        # Get the maximum value in the 'Score' column
        max_score = df['score'].max()
        max_rows = df[df['score'] == max_score].to_dict('records')
        if max_score == 0:
            return max_rows[0], df
        max_pos = 0
        max_row = {}
        for row in max_rows:
            raw_address = self.preprocess_text(raw_address)
            row[type_address] = self.preprocess_text(row[type_address])
            address = visen.remove_tone(raw_address)
            db_address = visen.remove_tone(row[type_address])
            common_grams = list(self.get_bigrams(address).intersection(self.get_bigrams(db_address)))
            common_word = common_grams[0][0]        
            pos = address.index(common_word)
            if pos >= max_pos:
                max_pos = pos
                max_row = row
        return max_row, df
    
    @staticmethod
    def remove_words_from_sentence(sentence):
        words_to_remove = ["quận", "thành phố", "đường", "phố", "xã", "phường", "huyện", "tỉnh",\
                            "quan", "thanh pho", "duong", "pho", "phuong", "huyen", "tinh", \
                            "số", 'thị xã', "ngõ", ",", ".", "district", "việt nam", "vietnam", "viet nam",\
                                "khu", "khu vực", "quanh"]
        pattern = r'(?:{})'.format('|'.join(map(re.escape, words_to_remove)))
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()

        short_words_to_remove = ["tp", 'p', 'q', "tx"]
        pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, short_words_to_remove)))
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()
        return re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()

    def extract_sub_address(self, address, type_address, source_df, threshold=0.9, **kwargs):
        norm_sub_address, _ = self.score_address(address, source_df, type_address, **kwargs)
        score = norm_sub_address['score']
        if score > threshold:
            id = norm_sub_address['id']
            sub_address = norm_sub_address[type_address]
            match = SequenceMatcher(
                None,
                visen.remove_tone(address).lower(),
                visen.remove_tone(sub_address).lower()
            ).find_longest_match(0, len(address), 0, len(sub_address))
            address = address[:match.a] + address[match.a + match.size :]
            return id, sub_address, address, norm_sub_address
        else:
            return 'None'
        
    def post_process(self, address_json):
        keys = list(address_json.keys())
        for key in keys:
            if not address_json[key]:
                address_json.pop(key)
        address_json["locationIds"] = {}
        if "id_street" in address_json:
            address_json["locationIds"]["streetId"] = address_json["id_street"]
            address_json["street"] = address_json["street"].title()
            address_json.pop("id_street")

        if "id_ward" in address_json:
            address_json["locationIds"]["wardId"] = address_json["id_ward"]
            address_json["ward"] = address_json["ward"].title()
            address_json.pop("id_ward")

        if "id_district" in address_json:
            address_json["locationIds"]["districtId"] = address_json["id_district"]
            address_json["district"] = address_json["district"].title()
            address_json.pop("id_district")
        
        if "id_province" in address_json:
            address_json["locationIds"]["cityId"] = address_json["id_province"]
            address_json["city"] = address_json["province"].title()
            address_json.pop("province")
            address_json.pop("id_province")
        
        return address_json

    def __call__(self, address) -> Any:
        address = address.replace(',','')
        address = address.replace('.','')
        norm_address = {}
        response = self.extract_sub_address(
            address=address,
            type_address='province',
            source_df=self.province,
        )
        if response != 'None':
            id_province, sub_address, address, last_address = response
            norm_address['province'] = sub_address
            norm_address["id_province"] = id_province

            address = self.remove_words_from_sentence(address)
            if address:               
                # Extract district
                response = self.extract_sub_address(
                    address=address,
                    type_address='district',
                    source_df=self.district,
                    id_province=id_province
                )
                if response != 'None':
                    id_district, sub_address, address, last_address = response
                    norm_address['district'] = sub_address
                    norm_address["id_district"] = id_district
                    address = self.remove_words_from_sentence(address)
                    if address:
                        norm_address = self.es.extract_given_location(
                            address=address,
                            address_json=norm_address,
                            given_location=["province", "district"]
                        )
                else:
                    norm_address = self.es.extract_given_location(
                        address=address,
                        address_json=norm_address,
                        given_location=["province"]
                    )
        else:
            # Extract district
            response = self.extract_sub_address(
                address=address,
                type_address='district',
                source_df=self.district
            )
            if response != 'None':
                id_district, sub_address, address, last_address = response
                norm_address['district'] = sub_address
                norm_address["id_district"] = id_district
                norm_address["id_province"] = last_address["id_province"]
                norm_address["province"] = self.id2province[norm_address["id_province"]]

                address = self.remove_words_from_sentence(address)
                if address:
                    norm_address = self.es.extract_given_location(
                        address=address,
                        address_json=norm_address,
                        given_location=["district"]
                    )
            else:
                norm_address = self.es.extract_given_location(
                    address=address,
                    address_json=norm_address,
                    given_location=[]
                )
        norm_address = self.post_process(norm_address)
        return norm_address