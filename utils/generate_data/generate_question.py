import random

def generate(
        price=None,
        address=None,
        type_sale=None,
        acreage=None,
        type_of_house=None,
        facede=None,
        number_of_bedrooms=None,
        road_width_in_front_of_house = None,
        the_direction_of_the_house=None,
    ):

    prompt = "Tìm "

    if type_sale != None:
        if type_sale == "Cần bán":
            prompt += "mua "
        if type_sale == "Cho thuê":
            prompt += "thuê "
        else:
            prompt = prompt + type_sale + " " 
    prompt += "nhà "

    if type_of_house != None:
        prompt += type_of_house

    if number_of_bedrooms != None:
        prompt += "{} phòng ngủ ".format(prompt)

    if price != None:
        prompt += random.choice(["giá ", "tài chính "])
        prompt += "{} ".format(price)

    if address != None:
        prompt += random.choice(["khu vực ", "ở "])
        prompt += address
    
    if acreage != None:
        prompt += random.choice(["rộng khoảng ", "diện tích "])
        prompt += acreage
    
    if facede != None:
        prompt += " mặt tiền khoảng {} ".format(facede)
    
    if road_width_in_front_of_house != None:
        prompt += "đường trước nhà rộng khoảng "
        prompt += road_width_in_front_of_house
    
    if the_direction_of_the_house != None:
        prompt += " ưu tiên nhà hướng "
        prompt += the_direction_of_the_house
    
    return prompt


if __name__ == "__main__":
    prompt = generate(
        price="{price}",
        address="{location}",
        type_sale="{type_sale}",
        facede="{facede}"
    )
    print(prompt)

