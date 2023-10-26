"""
Generate the candidates
"""
import re

import numpy as np
import pandas as pd

from tqdm import tqdm
from thefuzz import fuzz
# from utils.generate_data.map_info_house import desc_to_question


def generate_house_searching_questions(house_info, question_templates):
    """
    Generate question by parse house's information to template

    Args:
        house_info: dict
            Contain info of a house like price, address, ...
        question_templates: list
            List of template question

    Return:
        List of dict information including keys:
            - question: used for train encoder
            - entity: used for calculate score
            - entity_question: used for entity extractor

    Example:
        >>> house_info = {
                "price": "4 tỷ",
                "address": "Hoàn Kiếm",
                "acreage": "100 m2",
            }
        >>> question_templates = [
                "Tôi muốn mua một ngôi nhà với giá khoảng {price} ở khu vực {address}",
                "Tìm nhà giá {price} ở {address} diện tích {acreage}."
            ]
        >>> generate_house_searching_questions(
                house_info=house_info,
                question_templates=question_templates
            )
        [
            {
                'question': 'Tôi muốn mua một ngôi nhà với giá khoảng 4 tỷ ở khu vực Hoàn Kiếm',
                'entity': ['price', 'address'],
                'entity_question': 'Tôi muốn mua một ngôi nhà với giá khoảng [4 tỷ](price) ở khu vực [Hoàn Kiếm](address)'
            },
            {
                'question': 'Tìm nhà giá 4 tỷ ở Hoàn Kiếm diện tích 100 m2.',
                'entity': ['price', 'address', 'acreage'],
                'entity_question': 'Tìm nhà giá [4 tỷ](price) ở [Hoàn Kiếm](address) diện tích [100 m2](acreage).'
            }
        ]
    """
    responses = []
    
    for template in question_templates:
        placeholders = re.findall(r'{([^{}]*)}', template)
        try:
            question = template.format(**house_info)
            if "không rõ" in question:
                continue
            for placeholder in placeholders:
                formatted_placeholder = f"[{house_info[placeholder]}]({placeholder})"
                template = template.replace("{" + placeholder + "}", formatted_placeholder)
            entity_question = template.format(**house_info)

            response = {
                "question": question,
                "entity": placeholders,
                "entity_question": entity_question
            }
            responses.append(response)
        except:
            pass
    return responses



# def score_numeric(
#         candidate_num,
#         needs_num,
#         penalty_upper=1,
#         penalty_lower=1
#     ):
#     """
#     This function to score ranking by compare 2 numeric variables

#     Args
#         candidate_num: (float) 
#     """
#     if np.isnan(candidate_num):
#         return 0.5
    
#     offset_score = np.abs(needs_num-candidate_num)/needs_num
#     if needs_num < candidate_num:
#         score = 1 - offset_score * penalty_upper
#     else:
#         score = 1 - offset_score * penalty_lower
    
#     if score < 0:
#         score = 0

#     return score

# weights = {
#     "acreage": 0.15,
#     "type_of_house":0.025,
#     "facede": 0.025,
#     "number_of_floors": 0.025,
#     "number_of_toilets": 0.025,
#     "number_of_bedrooms": 0.1,
#     "price": 0.3,
#     "address": 0.35,
# }

# # Define the similarity function
# def text_score(x, query):
#     score = fuzz.token_set_ratio(x, query) 
#     if score < 90:
#         return 2/900 * score
#     else:
#         return 1/100 * score
    
# def score_candidate(
#         df: pd.DataFrame,
#         price=None,
#         address=None,
#         acreage=None,
#         type_of_house=None,
#         facede=None,
#         num_bedrooms=None,
#         num_toilets=None,
#         num_floors=None
#     ):

#     """
#     This function retrieval data candidate for a question and score candidate base on 
#     the features given on these question

#     Args
#         df: (DataFrame) data frame source contains all house
#         price: house's price is given in the question
#         acreage: house's acreage is given in the question
#         num_bedrooms: number of bedrooms is given in the question
#         facede: house's facede is given in the question
    
#     """
    
#     candidate_df = df.copy(deep=True)

#     candidate_df['score'] = 0
#     for key in weights:
#         candidate_df['{}_score'.format(key)] = 0

#     if address != None:
#         candidate_df["address_score"] = candidate_df['address'].apply(lambda x: text_score(x, address))

#         pos_address = candidate_df[candidate_df["address_score"] > 0.5]
#         neg_address = candidate_df[candidate_df["address_score"] < 0.5]
#         if len(neg_address) > 2 * len(pos_address):
#             neg_address = neg_address.sample(2 * len(pos_address), random_state=100)
        
#         candidate_df = pd.concat([pos_address, neg_address], ignore_index=True)

#     else:
#         weights['address'] = 0
    

#     if type_of_house != None:
#         candidate_df.loc[candidate_df["type_of_house"]==type_of_house, 'type_of_house_score'] = 1
#         candidate_df.loc[candidate_df["type_of_house"]!=type_of_house, 'type_of_house_score'] = 0
#     else:
#         weights["type_of_house"] = 0

    
#     numeric_features = {
#         "price": {
#             "value": price,
#             "penalty_upper": 0.85,
#             "penalty_lower": 0.8
#         },
#         "acreage": {
#             "value": acreage,
#             "penalty_upper": 0.85,
#             "penalty_lower": 0.8
#         },
#         "facede": {
#             "value": facede,
#             "penalty_upper": 0.85,
#             "penalty_lower": 0.8
#         },
#         "number_of_bedrooms": {
#             "value": num_bedrooms,
#             "penalty_upper": 2,
#             "penalty_lower": 2
#         },
#         "number_of_toilets": {
#             "value": num_toilets,
#             "penalty_upper": 2,
#             "penalty_lower": 2
#         },
#         "number_of_floors": {
#             "value": num_floors,
#             "penalty_upper": 2,
#             "penalty_lower": 2
#         }
#     }


#     for name_feature, feature in numeric_features.items():
#         if feature["value"] != None:
#             candidate_df["{}_score".format(name_feature)] = candidate_df[name_feature].apply(
#                 lambda num: score_numeric(
#                     candidate_num=num,
#                     needs_num=feature["value"],
#                     penalty_upper=feature["penalty_upper"],
#                     penalty_lower=feature["penalty_lower"]
#                 )
#             )
#         else:
#             weights[name_feature] = 0

#     sum_weight = 0
#     for feature in weights:
#         sum_weight += weights[feature]
#         feature_score = weights[feature] * candidate_df["{}_score".format(feature)]
#         candidate_df["score"] += feature_score
#     candidate_df["score"] /= sum_weight
        
#     return candidate_df.sort_values(by='score', ascending=False)


# def generate_candidate(query: pd.Series, source_df, max_pos, max_neg):
    
#     query = query.fillna(np.nan).replace([np.nan], [None])
#     all_candidate = score_candidate(
#         df=source_df,
#         price=query["price"],
#         address=query["address"],
#         acreage=query["acreage"],
#         type_of_house=query["type_of_house"],
#         facede=query["facede"],
#         num_bedrooms= query["number_of_bedrooms"],
#         num_floors=query["number_of_floors"],
#         num_toilets=query["number_of_toilets"],
#     )

#     pos_candidate = all_candidate[all_candidate["score"] >= 0.5]
#     if max_pos < len(pos_candidate):
#         # pos_candidate = pos_candidate.iloc[:max_pos]
#         pos_candidate = pos_candidate.sample(max_pos, random_state=100)
    
#     neg_candidate = all_candidate[all_candidate["score"] < 0.5]
#     if max_neg < len(neg_candidate):
#         neg_candidate = neg_candidate.sample(max_neg, random_state=100)

#     return pos_candidate, neg_candidate

# def generate_answer(raw_df, source_df, num_root_pairs, max_pos, max_neg):


#     root_pair = source_df.sample(num_root_pairs, random_state=100)
#     list_pair = []
    
#     for _, row in tqdm(root_pair.iterrows(), total=root_pair.shape[0], colour="green"):
#         pos_candidate, neg_candidate = generate_candidate(
#             query=row,
#             source_df=source_df,
#             max_pos=max_pos,
#             max_neg=max_neg
#         )
#         candidate = pd.concat([pos_candidate, neg_candidate], ignore_index=True)
#         candidate = pd.merge(
#             left=candidate,
#             right=raw_df[["_id", "std_desc"]],
#             on="_id",
#             how="left"
#         )
    
#         scores = candidate["score"].tolist()
#         house_id = candidate["_id"].tolist()
#         answers = candidate["std_desc"].tolist()

#         desc = raw_df[raw_df["_id"]==row["_id"]].iloc[0]["std_desc"]
#         questions = desc_to_question(desc)
#         num_candidate = len(candidate)
#         num_questions = len(questions)
#         offset = num_candidate % num_questions
#         questions = questions * (num_candidate // num_questions) + questions[:offset]

#         pair = {
#             "question_id": [row["_id"]] *  num_candidate,
#             "question": questions,
#             "answer": answers,
#             "score": scores,
#             "house_id": house_id
#         }
#         pair = [dict(zip(pair, t)) for t in zip(*pair.values())]
#         list_pair.extend(pair)

#     return list_pair
