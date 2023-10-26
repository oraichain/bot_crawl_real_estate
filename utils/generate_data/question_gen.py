def price_address(price, address):
    questions = [
        f"Tôi muốn mua một ngôi nhà với giá khoảng {price} ở khu vực {address}.",
        f"Tìm nhà giá khoảng {price} ở {address}.",
        f"Muốn tìm mua một ngôi nhà giá cả nằm trong khoảng {price} tại khu vực {address}.",
        f"Tôi đang tìm  một ngôi nhà có giá dao động trong khoảng {price} ở khu vực {address}.",
        f"Tôi đang cố gắng tìm mua một căn nhà giá khoảng {price} tại {address}.",
        f"Đang có nhu cầu mua một ngôi nhà với mức giá khoảng {price} tại khu vực {address}.",
        f"Tôi đang muốn tìm mua một căn nhà có giá không quá {price} tại khu vực {address}.",
        f"Tôi đang tìm mua một ngôi nhà ở khu vực {address} với giá dao động trong khoảng {price}.",
        f"Tôi đang muốn mua một căn nhà tại {address} với giá khoảng {price}.",
        f"Tôi đang tìm  một căn nhà giá không vượt quá {price} ở khu vực {address}.",
        f"Tìm nhà khu vực {address}, tài chính khoảng {price}",
        f"Tài chính {price}, tìm nhà khu vực {address}",
        f"Tôi đang tìm mua căn nhà ở {address} với mức giá khoảng {price}.",
        f"Tôi đang tìm  một ngôi nhà ở {address} với mức giá khoảng {price}.",
        f"Tôi đang cần mua một căn nhà ở {address} với giá trong khoảng {price}.",
        f"Tôi muốn tìm một ngôi nhà ở {address} có giá ước tính là {price}.",
        f"Tôi đang tìm một căn nhà với giá ước tính khoảng {price} tại {address}.",
        f"Tôi đang tìm  một ngôi nhà ở {address} với mức giá khoảng {price}.",
        f"Tôi đang tìm một căn nhà ở {address} với giá dao động trong khoảng {price}.",
        f"Tôi đang tìm  một ngôi nhà ở {address} có giá không quá {price}."
    ]
    
    return questions


def price_acreage(price, acreage):
    question = [
        f"Tôi muốn mua một căn nhà có diện tích {acreage} và giá khoảng {price}, bạn có thể giúp tôi tìm kiếm được không.",
        f"Cho biết những căn nhà nào có diện tích {acreage} và giá khoảng {price} đang bán.",
        f"Tìm kiếm những ngôi nhà có diện tích {acreage} và giá khoảng {price} trong khu vực này.",
        f"Có những căn nhà nào có giá tầm {price} và diện tích {acreage} đang được bán ở khu vực này không.",
        f"Tôi đang tìm mua một căn nhà có giá tầm {price} và diện tích {acreage}, bạn có thể giới thiệu cho tôi những lựa chọn nào.",
        f"Tìm kiếm các ngôi nhà có giá khoảng {price} và diện tích {acreage} đang bán ở khu vực này.",
        f"Tôi muốn tìm mua một căn nhà ở khu vực này với giá tầm {price} và diện tích {acreage}, bạn có thể giúp tôi được không.",
        f"Cho biết những căn nhà có giá tầm {price} và diện tích {acreage} đang được bán ở khu vực này.",
        f"Tôi cần mua một căn nhà có diện tích {acreage} và giá khoảng {price} ở đây, bạn có thể giúp tôi tìm kiếm được không.",
        f"Tìm kiếm những căn nhà có giá khoảng {price} và diện tích {acreage} ở khu vực này.",
        f"Tôi muốn mua một căn nhà có diện tích {acreage} và tài chính tầm {price}, bạn có thể giúp tôi tìm kiếm được không.",
        f"Có những căn nhà nào có diện tích {acreage} và giá tầm {price} đang bán ở khu vực này không."
    ]

    return question


def address_acreage(address, acreage):
    question = [
        f"Cho biết những căn nhà có diện tích khoảng {acreage} trong khu vực {address}.",
        f"Có nhà nào có diện tích khoảng {acreage} đang bán ở {address} không.",
        f"Tôi muốn tìm một căn nhà có diện tích {acreage} ở {address}, bạn có thể giúp tôi được không.",
        f"Tìm nhà có diện tích {acreage} trong khu vực {address} đang bán.",
        f"Tôi đang tìm mua một ngôi nhà có diện tích {acreage} tại {address}, bạn có thể giới thiệu cho tôi được không.",
        f"Tìm những căn nhà rộng {acreage} nằm ở {address}.",
        f"Cho biết những căn nhà đang được bán ở {address} có diện tích khoảng {acreage}.",
        f"Tôi cần tìm một ngôi nhà có diện tích {acreage} ở {address}, có thể cho tôi biết những căn nhà như vậy đang bán không.",
        f"Tìm các ngôi nhà rộng khoảng {acreage} đang bán ở {address}.",
        f"Bạn có thể giúp tôi tìm một căn nhà có diện tích {acreage} ở {address} không.",
        f"Tôi đang tìm  một ngôi nhà có diện tích {acreage} ở {address}, bạn có thể giúp tôi được không.",
        f"Tôi đang tìm mua nhà ở {address} với diện tích {acreage}, bạn có thể giới thiệu cho tôi được không.",
        f"Có những căn nhà nào có diện tích {acreage} đang bán ở khu vực {address} không.",
        f"Tôi muốn mua một ngôi nhà ở {address} có diện tích {acreage}, bạn có thể cho tôi biết có những lựa chọn nào không.",
        f"Tôi cần mua một căn nhà có diện tích {acreage} ở {address}, bạn có thể giúp tôi tìm  được không.",
        f"Tìm  những ngôi nhà có diện tích {acreage} ở {address} đang được bán.",
        f"Tôi đang muốn mua một căn nhà ở khu vực {address} với diện tích {acreage}, có thể giới thiệu cho tôi những lựa chọn nào không.",
        f"Có những ngôi nhà có diện tích {acreage} đang được bán ở khu vực {address} không.",
        f"Tôi đang tìm một căn nhà có diện tích {acreage} để mua ở {address}, bạn có thể giúp tôi tìm  được không.",
        f"Cho biết những căn nhà có diện tích {acreage} đang bán ở khu vực {address}."
    ]

    return question
price_address(
    price="5 tỷ",
    address="Láng Hạ"
)
    