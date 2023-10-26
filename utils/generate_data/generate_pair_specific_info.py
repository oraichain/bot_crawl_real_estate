# Create pair question + bio house
from pathlib import Path

import pandas as pd

question_rent = Path("data/question/thue.txt").read_text().splitlines()[:20]
question_sell = Path("data/question/mua.txt").read_text().splitlines()[:20]

table_rent = pd.DataFrame({
    "question": question_rent,
    "question_id": ["rent_{}".format(i) for i in range(len(question_rent))]
})

table_sell = pd.DataFrame({
    "question": question_sell,
    "question_id": ["sell_{}".format(i) for i in range(len(question_sell))]
})

# table_rent.to_csv("data/question/question_rent.csv", index=False)
# table_sell.to_csv("data/question/question_sell.csv", index=False)

df = pd.read_csv("data/netstock/update_1804.csv")
house_sell = df[df['type_sale'] == "Cần bán"]
house_rent = df[df['type_sale'] == "Cho thuê"]

top_sell = house_sell.sample(1000, random_state=1)[['_id', 'bio']].rename(columns={"_id": "house_id"})
top_rent = house_rent.sample(1000, random_state=1)[['_id', 'bio']].rename(columns={"_id": "house_id"})

pair_sell = pd.merge(table_sell, top_sell, how='cross')
pair_rent = pd.merge(table_rent, top_rent, how='cross')

pair_sell.sort_values(by=['question_id', 'house_id'], inplace=True)
pair_rent.sort_values(by=['question_id', 'house_id'], inplace=True)

pair_sell.to_csv("data/conversation/top_20_question_1000_house_random_state_1/pair_sell_0_20_question_1000_house_random_1.csv", index=False)
pair_rent.to_csv("data/conversation/top_20_question_1000_house_random_state_1/pair_rent_0_20_question_1000_house_random_1.csv", index=False)



# Addition rerun when encountering exception

def addition_offset(df, file_curr, out_remain):
    curr_ans = pd.read_json(file_curr, lines=True)
    df['id_ans'] = df['question_id'] + "_" + df['house_id']
    curr_ans['id_ans'] = curr_ans['question_id'] + "_" + curr_ans['house_id']
    remain_df = df[~ df['id_ans'].isin(curr_ans['id_ans'])]
    
    remain_df.to_csv(out_remain, index=False)
    return remain_df
    

df = pd.read_csv("data/conversation/top_20_question_1000_house_random_state_1/pair_sell_0_20_question_1000_house_random_1.csv").iloc[18000:200000]

addition_offset(
    df,
    file_curr="data/conversation/top_20_question_1000_house_random_state_1/answer_sell/_18000_20000_answer_pair_sell_0_20_question_1000_house_random_1.json",
    out_remain="data/conversation/top_20_question_1000_house_random_state_1/offset_18k_20k.csv"
)


import json
def load_json(file_name):
    with open(file_name, 'r') as fi:
        return [json.loads(row) for row in fi]


def save_json(df, out_file):
    df.to_json(
        path_or_buf=out_file,
        orient="records",
        force_ascii=False, 
        indent=4
    )