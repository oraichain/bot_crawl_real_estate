# Intent
INTENT_CLASSIFICATION_THRESHOLD = 0.5
FIND_HOUSE = "search_re"
EVAL_PRICE = "eval_price"
ASK_DETAIL = "ask house's info"
ASK_FLOW_SELL = "ask_flow_sell"
ASK_FLOW_BUY = "ask_flow_buy"
GENERAL_LAW = "general_law"
ASK_FENGSHUI = "ask_fengshui"
SEARCH_INFO = "search_info"
EVAL_AREA = "eval_area"
EVAL_POTENTIAL = "eval_potential"
UNCLEAR = "unclear"
ASK_REDEVELOPMENT = "ask_redevelopment"
SELL_PROPERTY = "sell_property"

# Purpose
BUY_HOUSE = "buy_house"
SELL_HOUSE = "sell_house"
INVEST = "invest"
ASK_MARKET = "ask_market"
FLOW_LAW = "flow_law" 

# Ner path
NER_PATH="models/ner/ner_xml_140k"
URL_NER="https://drive.google.com/file/d/1j53yDW82yf86i83G1H99oXblEiQLoLQj/view?usp=sharing"

# Classifier path
CLASSIFIER_PATH = "models/classifier/multi_intent/multi_intent_1.7.pt"
URL_CLASSIFIER = "https://drive.google.com/uc?id=1LB5djIH559GXeiTFWzicPVnh-GWmoj5X"

PRICE_CLS_PATH = "models/classifier/price_cls/price_cls_1.pt"
URL_PRICE_CLS = "https://drive.google.com/uc?id=1tAONtLDYWgtQkEywOX4jZm1vbRQ9MzTW"

# Law retrieval path
BI_ENCODER_PATH = "models/law_retrieval/xml_law"
URL_BI_ENCODER = "https://drive.google.com/file/d/1DOsFWeUNImlvRX_AsWI036vGKErYvSXQ/view?usp=sharing"
LAW_DATA_PATH = "data/law_retrieval/v1.2_law.csv"
LAW_CONSTRUCTION_DATA_PATH = "data/law_retrieval/law_gov.json"

# KOL retrieval path
KOL_BI_ENCODER_PATH = "models/kol_retrieval/phobert2_kol"
URL_KOL_BI_ENCODER = "https://drive.google.com/file/d/1-kcOTUo89awZXgJdMDPYcx5fOa0T2jIw/view?usp=sharing"
KOL_DATA_PATH = "data/kol/kol.csv"
URL_KOL_DATA  = "https://drive.google.com/file/d/1DChggHHS9Hjc7GtlXeN4ocqQwgYC8HBL/view?usp=sharing"
KOL_EMBEDDINGS_PATH = "data/kol/kol_embeddings.npz"
URL_KOL_EMBEDDINGS = "https://drive.google.com/file/d/1UkAnqqZzVTmzbYgchx1UFN39iJRdLxUT/view?usp=sharing"

# Number of question recommends
NUM_QUESTION_RECOMMENDS = 3

# Elastic search
ES_IP = "http://125.212.192.225:9200/neststock-address"
ES_USER = "elastic"
ES_PASSWORD = "Abc@123"

# DIRECTION
NORTH = "north"
SOUTH = "south"
EAST = "east"
WEST = "west"
NORTHEAST = "northeast"
NORTHWEST = "northwest"
SOUTHEAST = "southeast"
SOUTHWEST = "southwest"