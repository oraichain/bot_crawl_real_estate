
import json
import requests

from extractor.base_extractor import BaseExtractor

class RasaExtractor(BaseExtractor):

    def __init__(self, host_rasa, do_preprocess=False):
        super().__init__(do_preprocess)
        self.url = host_rasa

    def __call__(self, question):
        data = {'text': question}

        response = requests.post(self.url, data=json.dumps(data))

        if response.status_code == 200:
            parsed_response = json.loads(response.content.decode('utf-8'))

            entities = {}
            for entity in parsed_response['entities']:
                entities[entity['entity']] = entity['value']
            
            return entities
        else:
            print('Request failed with status code:', response.status_code)
            return None
