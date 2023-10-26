import json
import pandas as pd
import visen
import re
from underthesea import word_tokenize
from difflib import SequenceMatcher

class AddressExtractor:

    def __init__(
        self,
        address_path="data/address/vn_address.json"
    ) -> None:
        with open(address_path, "r") as file:
            json_address = json.load(file)
        self.province = pd.DataFrame(json_address["province"])
        self.district = pd.DataFrame(json_address["district"])
        self.ward = pd.DataFrame(json_address["ward"])
    
        self.id2province = dict(zip(self.province['id'], self.province['province']))
        self.id2district = dict(zip(self.district['id'], self.district['district']))
        self.id2ward = dict(zip(self.ward['id'], self.ward['ward']))

    @staticmethod
    def preprocess_text(text):
        text = " ".join(word_tokenize(text)).strip()
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

    @staticmethod
    def extract_numbers(text):
        return re.findall(r'\d+', text)

    @staticmethod
    def remove_numbers(text):
        return re.sub(r'\d+', '', text)

    def score_address(self, raw_address, source_address, type_address, **kwargs):
        df = source_address.copy()
        if kwargs:
            id_type, id = list(kwargs.items())[0]
            df = df[df[id_type]==id].reset_index(drop=True)
        # df['score'] = df[type_address].apply(lambda text: fuzz.token_set_ratio(raw_address, text))
        df['score'] = df[type_address].apply(lambda text: self.compare_texts(raw_address, text))

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
                            "số", 'thị xã', "ngõ", ",", ".", "district", "việt nam", "vietnam", "viet nam"]
        pattern = r'(?:{})'.format('|'.join(map(re.escape, words_to_remove)))
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()

        short_words_to_remove = ["tp", 'p', 'q', "tx"]
        pattern = r'\b(?:{})\b'.format('|'.join(map(re.escape, short_words_to_remove)))
        sentence = re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()
        return re.sub(pattern, '', sentence, flags=re.IGNORECASE).strip()

    @staticmethod
    def remove_sub_address(sub_address, text):
        return re.sub(r'\b(?:{})\b'.format(sub_address), '', text, count=1, flags=re.IGNORECASE).strip(',. ')

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

    def __call__(self, address):
        norm_address = {}
        last_address = {}
        # Extract province
        response = self.extract_sub_address(
            address=address,
            type_address='province',
            source_df=self.province,
        )
        if response != 'None':
            id_province, sub_address, address, last_address = response
            norm_address['province'] = sub_address
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
                # Extract ward
                response = self.extract_sub_address(
                    address=address,
                    type_address='ward',
                    source_df=self.ward,
                    id_district=id_district
                )
                if response != 'None':
                    id_ward, sub_address, address, last_address = response
                    norm_address['ward'] = sub_address             
            else:
                # Extract ward
                response = self.extract_sub_address(
                    address=address,
                    type_address='ward',
                    source_df=self.ward,
                    id_province=id_province
                )
                if response != 'None':
                    id_ward, sub_address, address, last_address = response
                    norm_address['ward'] = sub_address      
        else:

            response = self.extract_sub_address(
                address=address,
                type_address='district',
                source_df=self.district
            )
            if response != 'None':
                id_district, sub_address, address, last_address = response
                norm_address['district'] = sub_address
                # Extract ward
                response = self.extract_sub_address(
                    address=address,
                    type_address='ward',
                    source_df=self.ward,
                    id_district=id_district
                )
                if response != 'None':
                    id_ward, sub_address, address, last_address = response
                    norm_address['ward'] = sub_address             
            else:
                # Extract ward
                response = self.extract_sub_address(
                    address=address,
                    type_address='ward',
                    source_df=self.ward
                )
                if response != 'None':
                    id_ward, sub_address, address, last_address = response
                    norm_address['ward'] = sub_address

        if last_address: 
            if 'province' not in norm_address and 'id_province' in last_address:
                norm_address['province'] = self.id2province[last_address['id_province']]
            if 'district' not in norm_address and 'id_district' in last_address:
                norm_address['district'] = self.id2district[last_address['id_district']]
            
        numbers = self.extract_numbers(address)
        number = '/'.join(numbers)
        address = self.remove_words_from_sentence(address)
        address = " ".join(address.split())
        street = re.sub(r'[^a-zA-ZÀ-ỹ, ]', '', address)
        street = street.strip(",. ")
        norm_address.update({"street": street})
        if number != '':
            norm_address.update({"number": number})
        if 'number' in norm_address and norm_address['street'] == '':
            if 'ward' in norm_address:
                norm_address['street'] = norm_address['ward']
                norm_address['ward'] = ''
            elif 'district' in norm_address:
                norm_address['street'] = norm_address['district']
                norm_address['district'] = ''
                norm_address['province'] = ''

        for key in norm_address:
            norm_address[key] = norm_address[key].title()
        
        if "province" in norm_address:
            norm_address["city"] = norm_address['province']
            norm_address.pop("province")
        return norm_address

