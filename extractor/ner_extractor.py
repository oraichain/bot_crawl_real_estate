import os
import re

from transformers import pipeline
from utils.helper_function import download_zip_folder

class NERExtractor:
    
    def __init__(self, ner_path, url_ner=None):
        if os.path.exists(ner_path):
            self.model = pipeline("ner", ner_path)
        else:
            dir_ner = os.path.dirname(ner_path)
            if not os.path.isdir(dir_ner):
                os.makedirs(dir_ner)
            download_zip_folder(url=url_ner, folder_path=os.path.dirname(ner_path))
            self.model = pipeline("ner", ner_path)
    
    @staticmethod 
    def parse_entities(output_dict):
        entities = {}
        for item in output_dict:
            entity = item['entity']
            word = item['word'].replace('▁', '')  # Remove the special token '▁' if present
            if entity.startswith('B-'):  # Beginning of a new entity
                entity_label = entity.split('-')[1]
                if entity_label not in entities:
                    entities[entity_label] = [word]
                else:
                    entities[entity_label].append(word)
            elif entity.startswith('I-'):  # Continuation of an existing entity
                entity_label = entity.split('-')[1]
                if entity_label in entities:
                    if item['word'].startswith('▁'):
                        entities[entity_label].append(word)
                    else:
                        entities[entity_label][-1] += word
        formatted_result = {label: ' '.join(words) for label, words in entities.items()}
        return formatted_result
    
    @staticmethod
    def adhoc_process(text):
        text = re.sub("Kiếm nhà", "kiếm nhà", text, flags=re.IGNORECASE)
        return text

    def __call__(self, text):
        if not text:
            return {}
        text = self.adhoc_process(text)
        entities = self.parse_entities(self.model(text))
        entities = dict(entities)
        for e_type in ["price", "acreage", "facede", "number_of_bedrooms", "number_of_toilets", "number_of_floors"]:
            if e_type in entities:
                entities.pop(e_type)
        return entities