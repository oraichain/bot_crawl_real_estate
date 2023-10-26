from extractor.address_extractor import AddressExtractor
import time
address_extractor = AddressExtractor()
t1 = time.time()
address_entities = address_extractor("Ngõ 104, ngách 35, 117 Đ. Cầu Giấy, Ngọc Khánh, Ba Đình, Hà Nội")
t2 = time.time()
print(address_entities)
print("Time: ", t2-t1)