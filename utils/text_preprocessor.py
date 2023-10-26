
import re
from typing import Any
import visen
from underthesea import word_tokenize
import py_vncorenlp
from unicodedata import normalize

from utils.helper_function import load_text
import re

def postprocess_text(text):
    text = " " + text
    # Define a regular expression pattern to match "number ."
    pattern = r'(?<=[^\n])\s*(\d+)\s*\.\s*'
    # Use re.sub to replace the matched patterns with "\nnumber ."
    text = re.sub(pattern, r'\n\1. ', text)
    text = text.replace("*", "\n*")

     # Define a regular expression pattern to match "number ."
    pattern = r'(?<=[^\n])\s*Bước (\d+)\s*'
    # Use re.sub to replace the matched patterns with "\nnumber ."
    text = re.sub(pattern, r'\nBước \1 ', text)
    
    # Other adhoc - post process
    text = text.replace('sổ red', 'sổ đỏ')

    return text.strip()

class TextSegmenter:

    def __init__(
        self,
        vncorenlp_dir='/Users/vincent/Documents/qacom/main/utils/vncorenlp'
    ):
        self.segmenter = py_vncorenlp.VnCoreNLP(
            annotators=["wseg"], 
            save_dir=vncorenlp_dir
        )

    def __call__(self, text) -> Any:
        return ' '.join(self.segmenter.word_segment(text))


class TextPreprocessor:
    def __init__(
            self, 
            lower=False,
            remove_punctuation=False,
            remove_num=False,
            segment=False, 
            remove_stopwords=False,
            stopwords_path="data/address/stopwords.txt",
            vncorenlp_dir='/Users/vincent/Documents/qacom/main/utils/vncorenlp'
        ):

        self.lower=lower
        self.do_remove_num=remove_num
        self.do_remove_punctuation = remove_punctuation
        self.do_segment = segment
        self.do_remove_stopwords =remove_stopwords
        if segment:
            self.segmenter = TextSegmenter(vncorenlp_dir=vncorenlp_dir)
        if remove_stopwords:
            self.stopwords = load_text(stopwords_path)
        
        self.acronym_map = {
            "pn": "phòng ngủ",
            "wc": "nhà vệ sinh",
            "mt": "mặt tiền",
            "lh": "liên hệ",
            "mp": "mặt phố",
            "dt": "diện tích",
            "kđt": "khu đô thị",
            "tp.": 'thành phố',
            'tp': 'thành phố',
            'bn': 'bao nhiêu',
            "oto": "ô tô",
            "trieu": "triệu",
            "nvs": "nhà vệ sinh",
            "vskk": "vệ sinh khép kín",
            "vs": "vệ sinh",
            'hcm': 'Hồ Chí Minh',
            'hn': 'Hà Nội',
            "láng hạ": "Láng Hạ",
            'sài gòn': 'Sài Gòn',
            'sg': "Sài Gòn",
            "M2": "m2",
            "mét vuông": "m2",
            "mét": "m",
            "đh": "đại học",
            "sđt": "số điện thoại",
            "đ/c": "địa chỉ",
            "đc": "địa chỉ",
            "ty": "tỷ",
            "tỉ": "tỷ",
            "Tỷ": "tỷ",
            'citỷ': 'city',
            'ko': 'không',
            'hồ gươm': 'hoàn kiếm',
            'bds': 'bất động sản',
            'bđs': 'bất động sản',
            "tt": "trung tâm",
            "tm": "thương mại",
            'siêu thị': 'siêu thị',
            'Nghĩa trang': 'ngĩa trang',
            'pccc': 'phòng cháy chữa cháy',
            'pc&cc': 'phòng cháy chữa cháy',
            'pc': 'phòng cháy',
            'Phòng': 'phòng',
            "ubnd": "ủy ban nhân dân",
            "thcs": "trung học cơ sở",
            "ccmn": "chung cư mini",
            "cc": "chung cư",
            "thpt": "trung học phổ thông",
            'ptcs': 'phổ thông cơ sở',
            "pk": "phòng khách",
            "t/c": "tài chính",
            "tc": "tài chính",
            'Phường': 'phường',
            'Đường': 'đường',
            'Quận': 'quận',
            'vm': 'Winmart',
            'wm': "Winmart",
            'Trường': 'trường',
            'Tiểu Học': 'tiểu học',
            'Phố': 'phố',
            'Ủy ban': 'ủy ban',
            'Công viên': 'công viên',
            'Đền': 'đền',
            'Chùa': 'chùa',
            'Chợ': 'chợ',
            'căn': 'căn nhà',
            'nhà  nhà': 'nhà',
            'công an': 'công an',
            'Thành phố': 'thành phố',
            'Bảo tàng': 'bảo tàng',
            'Trung tâm': 'trung tâm',
            'Hoàng Mai': 'Hoàng Mai',
            'Long Biên': 'Long Biên',
            'Thanh Xuân': 'Thanh Xuân',
            'Bắc Từ Liêm': 'Bắc Từ Liêm',
            'Ba Đình': 'Ba Đình',
            'Cầu Giấy': 'Cầu Giấy',
            'Đống Đa': 'Đống Đa',
            'Hai Bà Trưng': 'Hai Bà Trưng',
            'Hoàn Kiếm': 'Hoàn Kiếm',
            'Hà Đông': 'Hà Đông',
            'Tây Hồ': 'Tây Hồ',
            'Hà Nội': 'Hà Nội'
        }

    @staticmethod
    def norm_money(text):
        # Define the pattern for matching numbers with decimal points or commas
        number_pattern = r'\b(\d+([.,]\d+)?)\b'
        
        # Find all occurrences of numbers with decimal points or commas
        numbers = re.findall(number_pattern, text)
        
        # Restore the numbers that were previously removed
        for num in numbers:
            text = text.replace(num[0], num[0].replace(',', '.'))

        # # Convert <number> tỷ <number> to <number>.<number> tỷ
        suffixs = 'triệu|tỷ|tầng|tang|phòng ngủ|phong ngu|ngu|ngủ|m2|m |nhà tắm|nha tam|tắm|-|đến|tới|\
phòng tắm|phong tam|tam|vệ sinh|nhà vệ sinh|nha ve sinh|ve sinh|khách|phòng khách|phong khạch|người|nguoi'
        match = re.search(f"(\d+)\s*tỷ\s*(\d+)\s*(triệu|trieu)?\s*({suffixs})?", text)
        if match:
            common_words = match.group()
            first_num = match.group(1)
            second_num = float(match.group(2))
            milion = match.group(3)
            suffix = match.group(4)
            if not suffix:
                if milion:
                    second_num/=100
                sub_text = f"{first_num}.{int(second_num)} tỷ"
                text = text.replace(common_words.strip(), sub_text)
        # Convert <number> tỷ rưỡi to <number>.5 tỷ
        text = re.sub(r'(\b\d+)\s*tỷ\s*rưỡi\b', r'\1.5 tỷ', text)
        
        # Convert <number>.0 to <number>
        text = re.sub(r"(\d+)\.0", r"\1", text)
        return text

    def convert_format(self, input_string):
        """ This function norm string like this: 3n1k to 3 phòng ngủ và 1 phòng khách"""
        pattern = r"(\d+)\s*n\s*(\d+)\s*k"
        match = re.search(pattern, input_string.lower())
        if match:
            num_bedrooms = match.group(1)
            num_other_rooms = match.group(2)
            output_string = f"{num_bedrooms} phòng ngủ và {num_other_rooms} phòng khách"
            return re.sub(pattern, output_string, input_string, flags=re.IGNORECASE)
        else:
            return input_string

    def replace_acronyms(self, text):
        text = self.convert_format(text)
        
        # Norm acronym and proper noun
        for acronym, full_form in self.acronym_map.items():
            text = re.sub(rf"\b{acronym}\b", f"{full_form} ", text, flags=re.IGNORECASE)
            # if acronym == "th":
            #     text = re.sub(rf"\b{acronym}\b", f"{full_form} ", text, flags=re.IGNORECASE)
            # else:
            #     text = re.sub(f"{acronym}", f"{full_form} ", text, flags=re.IGNORECASE)

        if "tỷ" in text:
            text = re.sub(r"(\d+)\s*[tT]\b", r"\1 tầng", text, flags=re.IGNORECASE)
        else:
            text = re.sub(r"(\d+)\s*[tT]\b", r"\1 tỷ", text, flags=re.IGNORECASE)
        text = re.sub(r"(\d+)\s*[tT][rR]\b", r"\1 triệu", text, flags=re.IGNORECASE)
        pattern = r"(\d+)\s*-\s*(\d+)"
        replacement = r"\1 đến \2"
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        text = re.sub("-", " ", text)
        text = re.sub(r"t(\d+)", r"tầng \1", text, flags=re.IGNORECASE)
        text = re.sub(",+", ",", text)
        text = " ".join(text.split())
        if 'tỷ ruoi' in text:
            text = text.replace('tỷ ruoi', 'tỷ rưỡi')
        text = self.norm_money(text)
        return text
    
    @staticmethod
    def norm_text(s):
        if type(s) == float:
            return 'Không rõ'
        s = s.split()
        s = [w.title() if w.isupper() else w for w in s]
        s = ' '.join(s)
        return s
    
    @staticmethod
    def remove_punctuation(text):
        text = re.sub(r'[^a-zA-ZÀ-ỹ0-9]+', ' ', text)
        return text

    @staticmethod
    def remove_num(text):
        text = re.sub(r'\d+', ' ', text)
        return text

    def __call__(self, text):
        # try:
        if self.do_remove_punctuation:
            text = self.remove_punctuation(text)
        if self.do_remove_num:
            text = self.remove_num(text)
        if (not self.do_remove_num) and (not self.do_remove_punctuation):
            text = text.replace("\n", ". ")
            text = text.replace("–", "-")
            text = visen.clean_tone(text)
            text = re.sub(r"[\u2013\u2014]", "-", text)
            text = re.sub(r'[^a-zA-ZÀ-ỹ0-9,\!\?\-/. \[\]\(\)]+', ' ', text)
        
        text = self.replace_acronyms(text)
        if self.do_segment:
            text = self.segmenter(text)
        text = self.norm_text(text)
        text = text.replace("đ .", "đường")
        text = text.replace("Sài Gòn", "Hồ Chí Minh")
        if self.lower:
            text = text.lower()
        if self.do_remove_stopwords:
            for word in self.stopwords:
                text = text.replace(word, "")
        text = " ".join(text.split())
        text = normalize("NFKC", text)
        return text

if __name__ == "__main__":
    # Example usage
    
    preprocess = TextPreprocessor(segment=False)
    import time
    s_time = time.time()
    text = 'tìm nhà 6-3 tỷ'
    print(preprocess(text))

    print(f'{time.time() - s_time}')
