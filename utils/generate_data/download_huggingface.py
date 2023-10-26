
import time
import requests
import os
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
from utils.measure_time import measure_time
import logging

class DatasetDownloader:
    def __init__(self):
        self.url = "https://datasets-server.huggingface.co/rows"
        self.params = {
            'dataset': 'Anthropic/hh-rlhf',
            'config': 'Anthropic--hh-rlhf',
            'split': 'train',
            'offset': '0',
            'limit': '100',
        }
        self.dataset_name = self.params["dataset"]
        self.exception_pages = []  # To store pages that encountered exceptions
        
    def download_page(self, page):
        try:
            self.params["offset"] = str((page - 1) * int(self.params["limit"]))
            response = requests.get(self.url, self.params)
            response.raise_for_status()  # Raise an exception for non-successful response status codes
            data = response.json()
            df_page = pd.DataFrame()
            for dict_row in tqdm(data["rows"]):
                df_row = self.convert_format(dict_row)
                df_page = pd.concat([df_page, df_row], ignore_index=True)
            
            return df_page
        
        except Exception as e:
            logging.error(f"Exception occurred while downloading page {page}: {e}")
            with open("data/huggingface/Anthropic/exception_page.txt", 'a') as fo:
                fo.write(str(page) + '\n')
            return None

    @staticmethod
    def convert_format(dict_row):
        id_dialogue = dict_row["row_idx"]
        text = dict_row["row"]["chosen"]
        pairs = text.split("Human: ")[1:]
        dialogue = {
            "Human": [],
            "Assistant": []
        }
        for pair in pairs:
            pair = pair.split("\n\nAssistant: ")
            dialogue["Human"].append(pair[0])
            dialogue["Assistant"].append(pair[1].rstrip("\n"))
        df_dialogue = pd.DataFrame(dialogue)
        df_dialogue["id_dialogue"] = id_dialogue

        return df_dialogue
    
    @measure_time
    def download_dataset(self, save_dir, num_pages=1, num_processes=2):
        save_dir = os.path.abspath(save_dir)
        os.makedirs(save_dir, exist_ok=True)
        


        with Pool(processes=num_processes) as pool:
            results = []
            for page in range(1, num_pages + 1):
                results.append(pool.apply_async(self.download_page, args=(page,)))
            
            for i, result in enumerate(results):
                df_page = result.get()
                if df_page is not None:
                    save_path = os.path.join(save_dir, f"{self.dataset_name}_page_{i+1}.csv")
                    df_page.to_csv(save_path, index=False)
                    print(f"Dataset '{self.dataset_name}' page {i+1} downloaded successfully to {save_path}")


if __name__ == "__main__": 
    downloader = DatasetDownloader()
    downloader.download_dataset(save_dir="data/huggingface/", num_pages=1608, num_processes=os.cpu_count())
