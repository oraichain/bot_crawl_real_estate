from transformers import AutoModelForTokenClassification
from underthesea import word_tokenize
from transformers import RobertaModel
from huggingface_hub import hf_hub_download
from importlib.machinery import SourceFileLoader
from collections import defaultdict

from extractor.base_extractor import BaseExtractor

class NERExtractor(BaseExtractor):
    def __init__(self, ner_path, do_preprocess=False):
        super().__init__(do_preprocess)

        self.model = AutoModelForTokenClassification.from_pretrained(ner_path)
        self.label2id = {
            'O': 0,
            'I-address': 2,
            'B-address': 1,
            'B-acreage': 3,
            'I-acreage': 4,
            'B-facede': 5,
            'I-facede': 6,
            'B-number_of_bedrooms': 7,
            'B-number_of_floors': 8,
            'B-number_of_toilets': 9,
            'B-price': 10,
            'I-price': 11,
            'B-the_direction_of_the_house': 12,
            'I-the_direction_of_the_house': 13,
            'B-type_of_house': 14,
            'I-type_of_house': 15
        }
        self.id2label = {v: k for k, v in self.label2id.items()}
        self.tokenizer = self._prepare_tokenizer()

    def _prepare_tokenizer(self):
        cache_dir='./cache_/'
        model_name='nguyenvulebinh/envibert'
        resources = ['envibert_tokenizer.py', 'dict.txt', 'sentencepiece.bpe.model']
        file_paths = []
        for item in resources:
            a = hf_hub_download(model_name, filename=item, cache_dir=cache_dir)
            file_paths.append(a)
        folder_path = '/'.join(file_paths[0].split('/')[:-1])
        tokenizer = SourceFileLoader("envibert.tokenizer", folder_path + "/envibert_tokenizer.py").load_module().RobertaTokenizer(folder_path)
        tokenizer.model_max_length=256
        return tokenizer

    def _tag_text(self, text):
        text = ' '.join(word_tokenize(text)).split()
        inputs = self.tokenizer(text, truncation=True, is_split_into_words=True, return_tensors='pt')
        outputs = self.model(**inputs)
        preds = outputs.logits.argmax(2)[0].tolist()
        words = self.tokenizer.convert_ids_to_tokens(inputs.input_ids[0])
        labels = [self.id2label[pred] for pred in preds]
        return words, labels, inputs.input_ids[0]

    def _convert_tokens_to_string(self, tokens):
        result = ""
        for token in tokens:
            if token.startswith("▁"):
                result += " " + token[1:]
            else:
                result += token
        return result.strip()

    def __call__(self, text):
        if not text:
            return {}
        words, labels, ids = self._tag_text(text)
        info = defaultdict(list)
        for _, label, idx in zip(words, labels, ids):
            if idx == self.tokenizer.cls_token_id or idx == self.tokenizer.sep_token_id:
                continue
            if label.startswith('B-'):
                entity = label[2:]
                info[entity].append(idx)
            elif label.startswith('I-'):
                entity = label[2:]
                info[entity].append(idx)
        for key, value in info.items():
            info[key] = self._convert_tokens_to_string(self.tokenizer.convert_ids_to_tokens(value))
        
        entities = dict(info)
        for e_type in ["price", "acreage", "facede", "number_of_bedrooms", "number_of_toilets", "number_of_floors"]:
            if e_type in entities:
                entities.pop(e_type)
        return entities
    
