import random 

class TemplatePrompt():
    intro = """Tôi là trợ lý chuyên tư vấn bất động sản, \
tôi có thể giúp bạn tìm nhà phù hợp, tham khảo giá cả thị trường bất \
động sản, trả lời các câu hỏi về pháp lý, quy trình thủ tục liên quan \
đến giao dịch mua bán bất động sản"""
    none_info = """Xin lỗi hiện tại mình chưa tạm thời chưa được cập nhật thông tin để trả lời bạn. Hi vọng lần tới gặp lại mình sẽ hỗ trợ bạn tốt hơn nha! """

class DefaultAnswerGenerator:
    def __init__(self) -> None:
        pass

    def ask_again(self) :
        text = ["Có vẻ như câu hỏi của bạn chưa cung cấp đầy đủ thông tin, bạn có thể hỏi lại không ?"]
        return random.choice(text)

    def end_dialogue(self) :
        text = ["Cảm ơn bạn đã quan tâm tới dịch vụ của Bất động sản GPT"]
        return random.choice(text)

    def ask_for_more_information(self):
        text = ["Bạn có thể cung cấp thêm nhiều thông tin hơn để có thể tìm nhà phù hợp cho bạn !",]
        return random.choice(text)