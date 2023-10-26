import requests

from OraiFlow.config import *

class ES:

    def __init__(
            self, 
            url=ES_IP, 
            username=ES_USER, 
            password=ES_PASSWORD
        ) -> None:
        self.url = url
        self.auth = (username, password)

    def post_process(self, address_json):
        key2pop = ['full_district', 'full_province', 'full_street', \
                   'full_ward', 'fullAddress', 'fullAddressNormalize']
        for k in key2pop:
            address_json.pop(k)
        return address_json
    
    def extract_given_location(self, address, address_json={}, given_location=[]):
        json_data = {
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": address,
                                        "fields": [
                                        "fullAddress",
                                        "fullAddressNormalize"
                                        ]
                                    }
                                }
                            ],
                            "must": [
                                {
                                    "match": {
                                        type_address: address_json[type_address]
                                    }
                                } for type_address in given_location
                            ]
                        }
                    },
                    "functions": [
                        {
                            "field_value_factor": {
                                "field": "weight",
                                "factor": 0.001,  
                                "missing": 0,
                                "modifier": "none"
                            }
                        }
                    ],
                    "boost_mode": "sum"
                }
            }
        }
        response = requests.get(
            url=f"{self.url}/_search",
            headers={'Content-Type': 'application/json'},
            json=json_data,
            auth=self.auth     
        )
        address_json = response.json()["hits"]['hits']
        if address_json:
            # Found list address appropriate
            address_json = address_json[0]["_source"]
            address_json = self.post_process(address_json)
        else:
            # Not found address respectively
            address_json = {}
        return address_json
    
    def get_all(self):
        json_data = {
            'query': {
                'match_all': {},
            },
        }
        response = requests.get(
            url=f"{self.url}/_search",
            headers={'Content-Type': 'application/json'},
            json=json_data,
            auth=self.auth     
        )
        if response.status_code == 200:
            return response.json()['hits']['hits']
        else:
            return "Empty index"
        
    def insert(self, json_data):
        response = requests.post(
            url=f"{self.url}/_doc",
            headers={'Content-Type': 'application/json'},
            json=json_data,
            auth=self.auth,
        )
    
    def delete(self):
        response = requests.delete(self.url, auth=self.auth)
        return response.json()


if __name__ == "__main__":

    es = ES()
    print(es.extract_given_location('8/3'))