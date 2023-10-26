import json
import os

import pandas as pd
from tqdm import tqdm

import secrets
import string

import shutil


def move_file(source_path, destination_path):
    try:
        # Move the file
        shutil.move(source_path, destination_path)
        print(f"File moved successfully from {source_path} to {destination_path}")
    except FileNotFoundError:
        print(f"Source file {source_path} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

        
def group_text(sentences, max_tokens = 400):
    sentences = list(dict.fromkeys([s.strip(" .") for s in sentences]))
    new_sentences = []
    current_group = ""
    for s in sentences:
        if len(current_group.split()) + len(s.split()) < max_tokens:
            current_group = current_group + ". " + s
        else:
            new_sentences.append(current_group.strip(". "))
            current_group = ""
    new_sentences.append(current_group.strip(". "))
    new_sentences = [s.strip() for s in new_sentences]
    new_sentences = [s for s in new_sentences if s]
    return new_sentences




def split_json_list(json_list, n):
    if n <= 0:
        raise ValueError("Number of smaller lists (n) must be greater than 0")
    # Calculate the number of JSON objects per smaller list
    objects_per_list = len(json_list) // n
    # Split the JSON list into smaller lists
    split_lists = [json_list[i:i+objects_per_list] for i in range(0, len(json_list), objects_per_list)]
    return split_lists


def generate_hash_id():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))


def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as fi:
        return fi.read().splitlines()

def save_text(file_path, text_list):
    with open(file_path, "w", encoding='utf-8') as file:
        
        # iterate through the text list and write each line to the file
        for line in text_list:
            file.write(line + "\n")

def load_csv_folder(folder_path):
    # Get a list of all CSV files in the folder
    csv_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".csv")]
    list_df = [pd.read_csv(file) for file in csv_files]
    return pd.concat(list_df, ignore_index=True)


# def load_json_file(file_path):
#     with open(file_path, "r") as file:
#         data = json.load(file)
#     return data

# import json

def load_json_exception(file_path):
    with open(file_path, 'r', encoding='utf8', errors='ignore') as fi:
        data = fi.read().splitlines()
    std_data = []
    for row in tqdm(data):
        try:
            std_data.append(eval(row))
        except:
            print(row)
    return std_data

def load_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as fi:
        return json.load(fi)

def load_json_file(file_path):
    data = []
    with open(file_path, "r", errors='ignore') as file:
        for line in file:
            row = json.loads(line)
            data.append(row)
    return data

def save_json_row(output_file, dict_obj, append=True):
    if append:
        format = "a"
    else:
        format = "w"
    with open(output_file, format) as file:
        json.dump(dict_obj, file, ensure_ascii=False)
        file.write("\n")        


def save_json_list(json_list, filename):
    with open(filename, 'w') as file:
        for item in tqdm(json_list, desc="Saving ..."):
            json_string = json.dumps(item, ensure_ascii=False)
            file.write(json_string + '\n')

import secrets
import string

def generate_api_key(length=12):
    """Generate a random API key."""
    alphabet = string.ascii_letters + string.digits + "-_"
    return ''.join(secrets.choice(alphabet) for _ in range(length))




import os
import pandas as pd

def split_file_to_dataframes(input_path, output_dir, chunk_size=100000):
    # Read the file into a dataframe
    df = pd.read_csv(input_path)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Split the dataframe into multiple smaller dataframes
    split_dataframes = []

    for i in range(0, len(df), chunk_size):
        split_dataframes.append(df[i:i+chunk_size])

    # Save each split dataframe to a separate file in the output directory
    for i, split_df in enumerate(split_dataframes):
        output_file = os.path.join(output_dir, f'split_file_{i}.csv')
        split_df.to_csv(output_file, index=False)



import os
import pandas as pd
from natsort import natsorted

def load_files_from_folder(folder_path):
    files = natsorted(os.listdir(folder_path))  # Sort files in folder using natural numeric sort
    dataframes = []

    for file in files:
        if file.endswith('.csv'):  # Load only CSV files
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)
    dataframes = pd.concat(dataframes, ignore_index=True)
    return dataframes


def delete_sentences_with_substring(passage, substring='Nhà gần với'):
    # Split the passage into sentences
    sentences = passage.split('. ')

    # Create a new list to store filtered sentences
    filtered_sentences = []

    # Iterate over each sentence and check for the substring
    for sentence in sentences:
        if substring not in sentence:
            filtered_sentences.append(sentence)

    # Join the filtered sentences back into a passage
    filtered_passage = '. '.join(filtered_sentences)

    return filtered_passage


import zipfile

def unzip_file(zip_path, extract_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    

import gdown
def download_file(url, destination_path):
    file_id = url.split("/")[5]
    base_url = 'https://drive.google.com/uc?id='
    url = base_url + file_id
    gdown.download(
        url=f'https://drive.google.com/uc?id={file_id}',
        output=destination_path,
    )

    if os.path.exists(destination_path):
        print(f"File '{destination_path}' downloaded to '{destination_path}'")

import os

def download_zip_folder(url, folder_path):
    # dir_folder = os.path.dirname(folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    zip_path = os.path.join(folder_path, "temp.zip")
    download_file(
        url=url,
        destination_path=zip_path
    )
    unzip_file(
        zip_path=zip_path,
        extract_dir=folder_path
    )
    os.remove(zip_path)    
    print("Successfully remove file {} from directory {}".format(zip_path, folder_path))