import requests
import random
import time
import visen
import numpy as np
from Levenshtein import distance

from OraiFlow.config import *
from OraiFlow.DefaultAnswerGenerator import *
from OraiFlow.House import House
# from writer.expert import Expert    # Viet's version KOL
from writer.llama2_writer import Llama2Writer
from writer.vi_llama2_writer import ViLlama2Writer
from extractor import Extractor
from mapping_key import Mapping
from intent_classifier.main import IntentClassifier
from utils.text_preprocessor import TextPreprocessor, postprocess_text
from retrieval.ensemble_law_retrieval import EnsembleRetrieval
from retrieval.kol_retrieval import KOLRetrieval


def post_process(entities, create_recommend=True):
    mapping = Mapping()
    mapped_result = {}
    for k in entities.keys():
        if (mapping.get_key(k) is not None) :
            mapped_result[mapping.get_key(k)] = entities[k]

    if create_recommend:
        entities = mapped_result.copy()
        if "city" in entities and entities["city"] != "Hà Nội":
            entities.pop("city")
            address_type = ["district", "ward", "street"]
            for e in address_type:
                if e in entities:
                    entities.pop(e)

        rest_entities = set(mapping.mapping.values()) - set(entities.keys())
        list_recommend = mapping.create_recommend(rest_entities, entities)
        return mapped_result, list_recommend
    else:
        return mapped_result


class AnswerGenerator:
    def __init__(
        self,
        ner_path=NER_PATH,
        url_ner=URL_NER,
        classifier_path=CLASSIFIER_PATH,
        url_classifier=URL_CLASSIFIER,
        price_cls_path=PRICE_CLS_PATH,
        url_price_lcs=URL_PRICE_CLS,
        bi_encoder_path=BI_ENCODER_PATH,
        url_bi_encoder_model=URL_BI_ENCODER,
        law_data_path=LAW_DATA_PATH,
        url_law_data=None,
        law_construction_data_path=LAW_CONSTRUCTION_DATA_PATH,
        num_question_recommends=NUM_QUESTION_RECOMMENDS,
        kol_bi_encoder_path=KOL_BI_ENCODER_PATH,
        kol_data_path=KOL_DATA_PATH,
        kol_url_model=URL_KOL_BI_ENCODER,
        kol_url_data=URL_KOL_DATA,
        kol_embeddings_path=KOL_EMBEDDINGS_PATH,
        kol_url_embeddings=URL_KOL_EMBEDDINGS
    ):
        self.extractor = Extractor(ner_path, url_ner, do_preprocess=False)

        self.intent_classifier = IntentClassifier(
            model_file=classifier_path,
            url_model=url_classifier
        )
        self.price_cls = IntentClassifier(
            model_file=price_cls_path,
            url_model=url_price_lcs
        )
        self.text_preprocess = TextPreprocessor()       
        self.default_answer_generator = DefaultAnswerGenerator()
        self.writer = Llama2Writer()
        self.vi_writer = ViLlama2Writer() 
        self.law_retrieval = EnsembleRetrieval(
            bi_encoder_path=bi_encoder_path,
            data_path=law_data_path,
            url_data=url_law_data,
            url_model=url_bi_encoder_model,
            law_construction_path=law_construction_data_path
        )
        
        # Viet's version KOL
        # self.expert = Expert()
        self.expert = KOLRetrieval(
            bi_encoder_path=kol_bi_encoder_path,
            data_path=kol_data_path,
            embeddings_path=kol_embeddings_path,
            url_model=kol_url_model,
            url_data=kol_url_data,
            url_embeddings=kol_url_embeddings
        )
        
        self.num_recommend = num_question_recommends

    @staticmethod
    def engsub_direction(direction):
        def fuzzy_sim(text1, text2):
            text1 = visen.remove_tone(text1.lower())
            return distance(text1, text2)
        map_direction = {
            "dong": EAST,
            "tay": WEST,
            "nam": SOUTH,
            "bac": NORTH,
            "dong bac": NORTHEAST,
            "tay bac": NORTHWEST,
            "dong nam": SOUTHEAST,
            "tay nam": SOUTHWEST

        }
        directions = ['dong', 'tay', 'nam', 'bac',\
                       'dong bac', 'tay bac', 'dong nam', 'tay nam']

        dis_list = list(map(lambda text: fuzzy_sim(text, direction), directions))
        norm_direction = directions[dis_list.index(min(dis_list))]
        norm_direction = map_direction[norm_direction]
        return norm_direction

    def response_find_house(self, message, intent, intent_confidence):
        # t0 = time.time()
        entities_message = self.extractor(message)
        if "the_direction_of_the_house" in entities_message:
            direction =  entities_message["the_direction_of_the_house"]
            entities_message["the_direction_of_the_house"] = self.engsub_direction(direction)
        entity_extracted, find_house_recommend = post_process(entities_message)
        info_recommends = [entities for _, entities in find_house_recommend]
        find_house_recommend = [s for s, _ in find_house_recommend]
        address_type = ["street", "ward", "district", "city"]
        address = [entity_extracted.get(a, "") for a in address_type]
        address = [a for a in address if a]
        address = ", ".join(address)
        # Recommend only Hanoi's area
        if "Hà Nội" not in address:
            address = None

        list_address = ['Hai Bà Trưng, Hà Nội', 'Đống Đa, Hà Nội', 'Thanh Xuân, Hà Nội',\
                                      'Hoàn Kiếm, Hà Nội', 'Cầu Giấy, Hà Nội']
        addition_info_recommend = random.choice(list_address)
        find_house_recommend.extend([
            f"Tìm mua nhà khu vực {addition_info_recommend}"
        ])
        addition_info_recommend = {
            "district": addition_info_recommend.split(", ")[0],
            "city": addition_info_recommend.split(", ")[1]
        }
        info_recommends.append(addition_info_recommend)
        default_recommend = [
            f"Cho tôi xem bản đồ quy hoạch khu vực {address if address else random.choice(list_address)}",
            f"Những căn nhà ở {address if address else random.choice(list_address)} thường có giá bao nhiêu?",
            "Mua nhà cần những thủ tục gì?"
        ]
        result = {}
        result["data"] = entity_extracted
        result["intent"] = {
            "intent" : intent,
            "intent_confidence" : intent_confidence
        } 
        # t1 = time.time()
        # print("s1 ", t1 - t0)
        def count_house(info):
            url = 'https://test.backend.neststock.orai.us/listings/properties/count'
            response = requests.get(url, info)
            num_house = response.json()["count"]
            return num_house
        list_recommend = []
        # print(find_house_recommend)
        for info, q in  zip(info_recommends, find_house_recommend):
            if count_house(info) > 0:
                list_recommend.append(q)
                break
        # print(list_recommend)
        list_recommend.extend(default_recommend)
        # t2 = time.time()
        # print("s2 ", t2 - t1)
        # print("Time pre compute recommend ", time.time() - s_time)
        num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)
        result['question_recommend'] = random.sample(list_recommend, num_recommend)
        return result 

    def ask_detail(self, obj_message):
        message = obj_message['question']
        message = self.text_preprocess(message)
        property = obj_message['property']
        house = House(property)
        bot_message = self.vi_writer(
            query=message,
            context=str(house)
        ).replace("Ely", "Bất Động Sản GPT")
        map_recommends = {
            "landSize": [
                "Nhà này rộng bao nhiêu?",
                "Diện tích của căn nhà này?"
            ],
            "price": [
                "Giá của ngôi nhà này?",
                "Nhà này bán giá bao nhiêu?"
            ],
            "city": [
                "Nhà này ở đâu thế ?",
                "Địa chỉ căn nhà này?"
            ],
            "numberOfFloors": [
                "Nhà này có mấy tầng?"
            ],
            "numberOfBathRooms": [
                "Nhà có bao nhiêu phòng tắm?"
            ],
            "numberOfBedRooms": [
                "Ngôi nhà có mấy phòng ngủ?"
            ],
            "houseDirection": [
                "Nhà này ngoảnh hướng nào?"
            ],
            "facade": [
                "Ngôi nhà có mấy mặt tiền?"
            ],
            "publicFacilities": ["Tiên ích - công viên, trường học xung quanh ngôi nhà này?", "Nhà có gần trường học nào không?"]
        }
        
        list_recommend = [random.choice(map_recommends[k]) for k in map_recommends if k in property]

        num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)

        question_recommend = random.sample(list_recommend, num_recommend)
        result = {
            "data": bot_message,
            "intent": {
                "intent": "ask_detail",
                "intent_confidence": 1
            },
            "question_recommend": question_recommend
        }
        return result

    @staticmethod
    def purpose_mining(list_intents, threshold=1.5):
        purposes = [BUY_HOUSE, SELL_HOUSE, INVEST, ASK_MARKET, FLOW_LAW]
        intents = [FIND_HOUSE, ASK_DETAIL, EVAL_PRICE, ASK_FLOW_SELL, ASK_FLOW_BUY, \
                ASK_FENGSHUI, EVAL_AREA, EVAL_POTENTIAL, SEARCH_INFO, \
                    ASK_REDEVELOPMENT, SELL_PROPERTY, GENERAL_LAW, UNCLEAR]
        weight_matrix = np.array([
            [1, 0, 0, 0, 0],
            [0.8, 0, 0.1, 0.1, 0],
            [0, 0, 0.1, 0.8, 0],
            [0, 0.8, 0, 0, 0.2],
            [0.8, 0, 0, 0, 0.2],
            [0, 0, 0, 0, 0],
            [0.2, 0, 0.8, 0, 0],
            [0.2, 0, 0.8, 0, 0],
            [0.2, 0.2, 0.2, 0.2, 0.2],
            [0.4, 0, 0.6, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0]
        ])
        weights = np.zeros(len(purposes))
        for intent in list_intents:
            index_intent = intents.index(intent)
            weights += weight_matrix[index_intent]
        purpose = "unclear"
        max_score = np.max(weights)
        if max_score >=  threshold:
            id_purpose = np.argmax(weights)
            purpose = purposes[id_purpose]
        return purpose

    def make_response(self, intent, intent_confidence, message) :
        res = {}
        res["intent"] = {"intent" : intent, "intent_confidence" : intent_confidence}
        res["data"] = message
        return res

    def get_response(self, data) :
        # t1 = time.time()
        last_message = data["question"]
        preprocessed_message = self.text_preprocess(last_message)
        intent, intent_confidence = self.intent_classifier(last_message)

        if intent_confidence < INTENT_CLASSIFICATION_THRESHOLD:
            intent = UNCLEAR
        
        if intent == UNCLEAR:
            bot_response = self.writer(
                query=preprocessed_message,
                context=TemplatePrompt.intro
            )
            # t4 = time.time()
            # print(f"Query: {preprocessed_message}\nContext: {TemplatePrompt.intro}")
            # print(f"Writer time: {round(t4 - t3, 3)}")
            bot_response = bot_response.replace("Ely", "Bất Động Sản GPT")
            entities = post_process(self.extractor(preprocessed_message.lower()), False)
            address_type = ["street", "ward", "district", "city"]
            address = [entities.get(a, "") for a in address_type]
            address = [a for a in address if a]
            address = ", ".join(address)
            if "Hà Nội" not in address:
                address = None
            list_recommend = [
                f"Mình muốn tìm các ngôi nhà ở khu vực {address if address else 'Hà Nội'}",
                "Quy trình thủ tục mua nhà gồm những gì?",
                f"Thông tin định giá nhà khu vực {address if address else 'Đống Đa'}",
                f"Tra cứu bản đồ quy hoạch khu vực {address if address else 'Cầu Giấy'}"
            ]
            if last_message in list_recommend:
                list_recommend.remove(last_message)
            bot_response = ". ".join(bot_response.split("."))

            num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)
            response = {
                "data": bot_response,
                "intent": {
                    "intent": UNCLEAR,
                    "intent_confidence": 1
                },
                "question_recommend": random.sample(list_recommend, num_recommend)
            }
            # t5 = time.time()
            # print(f"Post process: {round(t5 - t4,3)}\n\n")

        elif intent in [GENERAL_LAW, ASK_FLOW_BUY, ASK_FLOW_SELL]:
            bot_response, law_reference, list_recommend = self.law_retrieval(preprocessed_message)
            # bot_response, law_reference, list_recommend = self.retrieval_law(preprocessed_message)
            num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)
            list_recommend.extend(
                [
                    "Tài chính 3 tỷ, tìm mua nhà khu vực Thanh Xuân, Hà Nội",
                    "Mình muốn tìm mua nhà khu vực quận Hai Bà Trưng",
                    "Cho mình xem bản đồ quy hoạch khu vực Đống Đa "
                ]
            )
            if last_message in list_recommend:
                list_recommend.remove(last_message)
            response = {
                "data": bot_response,
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                },
                "question_recommend": random.sample(list_recommend, num_recommend),
                "law_reference": law_reference
            }
        
        elif intent == ASK_REDEVELOPMENT:
            entities = post_process(self.extractor(preprocessed_message), False)
            address_type = ["street", "ward", "district", "city"]
            address = [entities.get(a, "") for a in address_type]
            address = [a for a in address if a]
            address = ", ".join(address)
            list_recommend = [
                "Những lưu ý khi mua nhà nằm trong diện quy hoạch?",
            ]
            rec_eval_price = f"Giúp mình định giá bất động sản khu vực {address if address else 'Đống Đa, Hà Nội'}."
            list_recommend.append(rec_eval_price)
            response = {
                "data": entities,
                "intent": {
                    "intent": ASK_REDEVELOPMENT,
                    "intent_confidence": intent_confidence
                },
                "question_recommend": list_recommend
            }
        
        elif intent == EVAL_PRICE:
            intent = EVAL_PRICE
            intent, intent_confidence = self.price_cls(last_message)
            if intent_confidence < 0.69:
                intent = EVAL_PRICE
                intent_confidence = 1
            entities = self.extractor(preprocessed_message)
            entities, list_recommend = post_process(entities, create_recommend=True)
            list_recommend = [s for s, _ in list_recommend]
            address_type = ["street", "ward", "district", "city"]
            address = [entities.get(a, "") for a in address_type]
            address = [a for a in address if a]
            address = ", ".join(address)
            if "Hà Nội" not in address:
                address = None

            list_recommend.extend([
                "Quy trình thủ tục mua bán nhà?",
                f"Mình muốn xem bản đồ quy hoạch khu vực {address if address else 'Đống Đa, Hà Nội'}",
                f"Tìm nhà 3 tỷ, khu vực {address if address else 'Thanh Xuân, Hà Nội'}",
            ])
            if last_message in list_recommend:
                list_recommend.remove(last_message)
            num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)
            response = {
                "data": entities,
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                },
                "question_recommend": random.sample(list_recommend, num_recommend)

            }

        elif intent == FIND_HOUSE or preprocessed_message.lower().startswith("tìm nhà"):
            intent == FIND_HOUSE
            response =  self.response_find_house(preprocessed_message, intent, intent_confidence)
            if (len(list(response["data"].keys())) <= 0) :
                response = self.make_response(
                    intent="ask house's info",
                    intent_confidence=0.1,
                    message=self.default_answer_generator.ask_for_more_information()
                )
                list_recommend = [
                    "Giúp mình tìm các ngôi nhà đang được bán ở khu vực Hà Nội",
                    "Tìm nhà 3 phòng ngủ, tài chính 4 tỷ"
                ]
                if last_message in list_recommend:
                    list_recommend.remove(last_message)
                response["question_recommend"] = list_recommend

        elif intent == ASK_FENGSHUI:
            response = {
                "data": "Tính năng này đang phát triển, quay lại sau.",
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                }
            }
        elif intent == SEARCH_INFO:
            bot_response = self.writer(
                query=preprocessed_message,
                context=""
            )
            bot_response = bot_response.replace("Ely", "Bất Động Sản GPT")
            response = {
                "data": bot_response,
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                }
            }
        elif intent ==  EVAL_AREA:
            response = {
                "data": "Tính năng này đang phát triển, quay lại sau.",
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                }
            }
        elif intent == EVAL_POTENTIAL:
            response = {
                "data": "Tính năng này đang phát triển, quay lại sau.",
                "intent": {
                    "intent": intent,
                    "intent_confidence": intent_confidence
                }
            }
        
        else :
            intent=UNCLEAR
            bot_response = self.writer(
                query=preprocessed_message,
                context=TemplatePrompt.intro
            )
            bot_response = bot_response.replace("Ely", "Bất Động Sản GPT")
            entities = post_process(self.extractor(preprocessed_message), False)
            address_type = ["street", "ward", "district", "city"]
            address = [entities.get(a, "") for a in address_type]
            address = [a for a in address if a]
            address = ", ".join(address)
            if "Hà Nội" not in address:
                address = None
            list_recommend = [
                f"Mình muốn tìm các ngôi nhà ở khu vực {address if address else 'Hà Nội'}",
                "Quy trình thủ tục mua nhà?",
                f"Thông tin định giá nhà khu vực {address if address else 'Đống Đa'}",
                f"Tra cứu bản đồ quy hoạch khu vực {address if address else 'Cầu Giấy'}"
            ]

            num_recommend = self.num_recommend if self.num_recommend < len(list_recommend) else len(list_recommend)
            if last_message in list_recommend:
                list_recommend.remove(last_message)
            bot_response = ". ".join(bot_response.split("."))
            response = {
                "data": bot_response,
                "intent": {
                    "intent": UNCLEAR,
                    "intent_confidence": 1
                },
                "question_recommend": random.sample(list_recommend, num_recommend)
            }
        # Don't use purpose mining
        # if "history_intents" in dialogue_data:
        #     dialogue_data["history_intents"].append(intent)
        #     history_intents = dialogue_data["history_intents"]
        # else:
        #     history_intents = [intent] 
        # purpose = self.purpose_mining(list_intents=history_intents)
        # response["purpose"] = purpose
        return response
    
    def ask_expert(self, question, expert_id):
        intent, _ = self.intent_classifier(question)
        question = self.text_preprocess(question)
        if intent == UNCLEAR:
            id2name = {
                'd63a4aa8-3499-463e-9640-0ea6fdf7726f': 'Rich Nguyễn',
                'b8f97557-290b-4d59-89bd-ff37281eb678': 'Nguyễn Thành Tiến',
                '3b87efdc-ef19-45d0-bd32-5da4e2266536': 'Trịnh Văn Mạnh',
                'cc7b93b7-df53-48b5-94bf-03f81e6c2691': 'Ngọc Ly',
                '32d216c6-b38b-4cfd-a34a-d2c9ca734f7a': 'Vũ Thanh Tuấn',
                '961078b1-3e30-4cc8-8240-e944e88131cd': 'Doctor Housing',
                '6b80ab16-3933-4b8c-8320-4f62c039cb9f': 'Hiển Lê BĐS',
                'ef48bdae-5132-425f-807b-0eb16439ebc7': 'Thuần Chu BĐS',
                'e1374e5d-e335-4c03-9965-682e9f3f66ba': 'Trần Minh',
                '8eadf32a-602d-4615-8aba-ab5449716e3d': 'Đoàn Dung',
                '2831c085-1b15-4091-af20-86d11b591b77': 'Minh Trần KTC'
            }
            if expert_id in id2name:
                name = id2name[expert_id]
            else:
                name = ""
            contexts = [
                "Xin chào, tôi là {}, một chuyên gia hàng đầu về lĩnh vực bất động sản, sẵn sàng để giải đáp các câu hỏi và chia sẻ kiến thức về bất động sản với bạn.",
                "Chào bạn, mình là {} - một chuyên gia tư vấn bất động sản, chuyên giải đáp những thắc mắc và chia sẻ kiến thức liên quan về bất động sản cho mọi người.",
                "Xin chào, rất vui được gặp bạn, mình là {}, một chuyên gia tư vấn bất động sản có nhiều năm kinh nghiệm, và mình mong muốn chia sẻ thông tin hữu ích về lĩnh vực này.",
                "Xin chào bạn, mình là {}, một chuyên gia trong lĩnh vực bất động sản, và mình rất vui được đồng hành cùng bạn để giải quyết mọi vấn đề liên quan đến bất động sản.",
                "Rất vui được gặp bạn, mình là {}, và nhiệm vụ của mình là giúp bạn tìm hiểu mọi điều về bất động sản một cách dễ dàng và chi tiết.",
                "Xin chào, hân hạnh được gặp bạn, mình là {}, chuyên gia tư vấn bất động sản với mong muốn chia sẻ kiến thức và kinh nghiệm của mình để bạn có cái nhìn rõ ràng hơn về thị trường này.",
                "Chào bạn, rất vui được gặp bạn, mình là {}, và mình hy vọng rằng thông qua sự hiểu biết và kinh nghiệm của mình, mình có thể giúp bạn hiểu rõ hơn về thế giới bất động sản.",
                "Chào bạn, mình là {}, một chuyên gia tư vấn bất động sản với mong muốn chia sẻ kiến thức và giúp bạn giải đáp mọi thắc mắc về lĩnh vực này.",
                "Xin chào, hân hạnh được gặp bạn, mình là {}, và mình đã dành nhiều thời gian để nghiên cứu và hiểu sâu về thế giới bất động sản, và mình muốn chia sẻ kiến thức đó với bạn.",
                "Rất vui được gặp bạn, mình là {}, một chuyên gia hàng đầu về bất động sản, và mình mong muốn mang lại giá trị cho bạn thông qua kiến thức của mình.",
                "Chào bạn, rất hân hạnh được gặp bạn, mình là {}, một chuyên gia tư vấn bất động sản, với nhiều năm kinh nghiệm trong lĩnh vực, mình sẽ giúp bạn giải đáp những thắc mắc trong phạm vi hiểu biết của mình.",
                "Rất vui được gặp bạn, mình là {}, và mình hy vọng rằng thông qua sự hiểu biết và kinh nghiệm của mình, mình có thể giúp bạn hiểu rõ hơn về thế giới bất động sản.",
                "Chào bạn, rất hân hạnh được gặp bạn, mình là {}, một chuyên gia tư vấn bất động sản với mong muốn chia sẻ kiến thức và giúp bạn giải đáp những thắc mắc về lĩnh vực này.",
                "Rất vui được gặp bạn, mình là {}, và mình sẽ cung cấp thông tin và sự hỗ trợ tốt nhất cho bạn.",
                "Chào bạn, rất hân hạnh được gặp bạn, mình là {}, một chuyên gia bất động sản với khả năng giải đáp mọi câu hỏi và chia sẻ kiến thức sâu rộng về lĩnh vực này.",
                "Rất vui được gặp bạn, tôi là {}, chuyên gia tư vấn bất động sản có kinh nghiệm, và tôi rất hạnh phúc được hỗ trợ bạn trong việc hiểu rõ hơn về lĩnh vực này.",
                "Chào bạn, rất hân hạnh được gặp bạn, tôi là {}, một chuyên gia với sứ mệnh làm cho kiến thức về bất động sản trở nên dễ hiểu và tiếp cận hơn cho mọi người.",
                "Rất vui được gặp bạn, tôi là {}, chuyên gia tư vấn bất động sản đầy nhiệt huyết, tôi hy vọng có thể đóng góp vào sự hiểu biết của bạn về thế giới bất động sản.",
                "Chào bạn, rất hân hạnh được gặp bạn, mình là {}, một chuyên gia bất động sản với khả năng giải đáp các câu hỏi và chia sẻ kiến thức sâu rộng về lĩnh vực này.",
                "Rất vui được gặp bạn, tôi là {}, chuyên gia tư vấn bất động sản, và tôi sẽ hỗ trợ tốt nhất cho bạn những vấn đề liên quan về bất động sản.",
                "Chào bạn, rất hân hạnh được gặp bạn, tôi là {}, một chuyên gia hàng đầu trong ngành bất động sản, và tôi rất vui được giúp đỡ bạn trong mọi vấn đề liên quan đến lĩnh vực này.",
                "Chào bạn, mình là {} - chuyên gia tư vấn bất động sản, chuyên giải đáp những thắc mắc và chia sẻ kiến thức liên quan về bất động sản cho mọi người",
                "Chào bạn, mình là {} - chuyên gia tư vấn bất động sản, chuyên giải đáp những thắc mắc và chia sẻ kiến thức liên quan về bất động sản cho mọi người"
            ]
            context = random.choice(contexts).format(name)
            val = None
            media_type=val
            link = val
            time_start = val
            response_dict = {
                "answer": context,
                "sourceLocation": time_start,
                "mediaLink": link,
                "mediaType": media_type,
                "recommends": [
                    "Những chiến lược đầu tư bất động sản thông minh"
                ],
                "otherExpertRecommends": [
                    {
                        "expertId": "d63a4aa8-3499-463e-9640-0ea6fdf7726f", 
                        "recommend": "Tình hình bất động sản Hà Nội hiện nay ?",
                    },
                    {
                        "expertId": "cc7b93b7-df53-48b5-94bf-03f81e6c2691", 
                        "recommend": "Nên mua nhà hay thuê nhà để tiền đầu tư ?",
                    }
                ],
                "full_content": ""
            }
            return response_dict


        # Viet's version kol 
        # response_expert = self.expert(question, expert_id)
        # response_dict = response_expert["result"]
        # if response_dict:
        #     if response_dict["answer"]:
        #         response_dict["answer"] = response_dict["answer"].replace("_", " ")
            
        #     recommends = list(set(response_dict["recommends"]))
        #     if len(recommends) > self.num_recommend:
        #         recommends = random.sample(recommends, self.num_recommend)
        #     response_dict["recommends"] = recommends

        # else:
        #     val = None
        #     answer = val
        #     media_type=val
        #     link = val
        #     time_start = val
        
        #     response_dict = {
        #         "answer": answer,
        #         "sourceLocation": time_start,
        #         "mediaLink": link,
        #         "mediaType": media_type,
        #         "recommends": [
        #             "Những chiến lược đầu tư bất động sản thông minh"
        #         ],
        #         "otherExpertRecommends": [
        #             {
        #                 "expertId": "d63a4aa8-3499-463e-9640-0ea6fdf7726f", 
        #                 "recommend": "Tình hình bất động sản Hà Nội hiện nay ?",
        #             },
        #             {
        #                 "expertId": "cc7b93b7-df53-48b5-94bf-03f81e6c2691", 
        #                 "recommend": "Nên mua nhà hay thuê nhà để tiền đầu tư ?",
        #             }
        #         ]
        #     }
        
        # New version KOL
        response_dict = self.expert(query=question, kol_id=expert_id)
        if response_dict["answer"] != None:
            context = response_dict["answer"]
            answer = self.vi_writer(
                query=question,
                context=context
            )
            answer = postprocess_text(answer)
            if "không có" in answer:
                answer = None
            response_dict["answer"] = answer
        return response_dict

    def classify(self, message) :
        intent, intent_confidence = self.intent_classifier(message)
        result = {}
        result["intent"]={"intent" : intent, "intent_confidence" : intent_confidence}
        return result