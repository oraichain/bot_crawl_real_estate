map_char = {
    "à": ["a", "f"], "á": ["a", "s"], "â": ["aa", ""], "ã": ["a", "x"], "è": ["e", "f"], "é": ["e", "s"],
    "ê": ["ee", ""], "ì": ["i", "f"], "í": ["i", "s"], "ò": ["o", "f"], "ó": ["o", "s"], "ô": ["oo", ""],
    "õ": ["o", "x"], "ù": ["u", "f"], "ú": ["u", "s"], "ý": ["y", "s"], "ă": ["aw", ""], "ĩ": ["i", "x"],
    "ũ": ["u", "x"], "ơ": ["ow", ""], "ư": ["uw", ""], "ạ": ["a", "j"], "ả": ["a", "r"], "ấ": ["aa", "s"],
    "ầ": ["aa", "f"], "ẩ": ["aa", "r"], "ẫ": ["aa", "x"], "ậ": ["aa", "j"], "ắ": ["aw", "s"], "ằ": ["aw", "f"],
    "ẳ": ["aw", "r"], "ẵ": ["aw", "x"], "ặ": ["aw", "j"], "ẹ": ["e", "j"], "ẻ": ["e", "r"], "ẽ": ["e", "x"],
    "ế": ["ee", "s"], "ề": ["ee", "f"], "ể": ["ee", "r"], "ễ": ["ee", "x"], "ệ": ["ee", "j"], "ỉ": ["i", "r"],
    "ị": ["i", "j"], "ọ": ["o", "j"], "ỏ": ["o", "r"], "ố": ["oo", "s"], "ồ": ["oo", "f"], "ổ": ["oo", "r"],
    "ỗ": ["oo", "x"], "ộ": ["oo", "j"], "ớ": ["ow", "s"], "ờ": ["ow", "f"], "ở": ["ow", "r"], "ỡ": ["ow", "x"],
    "ợ": ["ow", "j"], "ụ": ["u", "j"], "ủ": ["u", "r"], "ứ": ["uw", "s"], "ừ": ["uw", "f"], "ử": ["uw", "r"],
    "ữ": ["uw", "x"], "ự": ["uw", "j"], "ỳ": ["y", "f"], "ỵ": ["y", "j"], "ỷ": ["y", "r"], "ỹ": ["y", "x"],
    "đ": ["dd", ""],
    "À": ["A", "f"], "Á": ["A", "s"], "Â": ["AA", ""], "Ã": ["A", "x"], "È": ["E", "f"], "É": ["E", "s"],
    "Ê": ["EE", ""], "Ì": ["I", "f"], "Í": ["I", "s"], "Ò": ["O", "f"], "Ó": ["O", "s"], "Ô": ["OO", ""],
    "Õ": ["O", "x"], "Ù": ["U", "f"], "Ú": ["U", "s"], "Ý": ["Y", "s"], "Ă": ["AW", ""], "Đ": ["DD", ""],
    "Ĩ": ["I", "x"], "Ũ": ["U", "x"], "Ơ": ["OW", ""], "Ư": ["UW", ""], "Ạ": ["A", "j"], "Ả": ["A", "r"],
    "Ấ": ["AA", "s"], "Ầ": ["AA", "f"], "Ẩ": ["AA", "r"], "Ẫ": ["AA", "x"], "Ậ": ["AA", "j"],
    "Ắ": ["AW", "s"], "Ằ": ["AW", "f"], "Ẳ": ["AW", "r"], "Ẵ": ["AW", "x"], "Ặ": ["AW", "j"],
    "Ẹ": ["E", "j"], "Ẻ": ["E", "r"], "Ẽ": ["E", "x"], "Ế": ["EE", "s"], "Ề": ["EE", "f"], "Ể": ["EE", "r"],
    "Ễ": ["EE", "x"], "Ệ": ["EE", "j"], "Ỉ": ["I", "r"], "Ị": ["I", "j"], "Ọ": ["O", "j"], "Ỏ": ["O", "r"],
    "Ố": ["OO", "s"], "Ồ": ["OO", "f"], "Ổ": ["OO", "r"], "Ỗ": ["OO", "x"], "Ộ": ["OO", "j"],
    "Ớ": ["OW", "s"], "Ờ": ["OW", "f"], "Ở": ["OW", "r"], "Ỡ": ["OW", "x"], "Ợ": ["OW", "j"],
    "Ụ": ["U", "j"], "Ủ": ["U", "r"], "Ứ": ["UW", "s"], "Ừ": ["UW", "f"], "Ử": ["UW", "r"], "Ữ": ["UW", "x"],
    "Ự": ["UW", "j"], "Ỳ": ["Y", "f"], "Ỵ": ["Y", "j"], "Ỷ": ["Y", "r"], "Ỹ": ["Y", "x"]
}


def sorting_key(tuple_item):
    return (-len(tuple_item[0]), -len(tuple_item[1]))

def keep_tuple(tuple_list):
    sorted_tuples = sorted(tuple_list, key=sorting_key)
    seen_chars = set()
    result = []
    seen_second_elements = set()

    for tuple_item in sorted_tuples:
        common_char = set(tuple_item[0]) & seen_chars
        if not common_char and tuple_item[1] not in seen_second_elements:
            result.append(tuple_item)
            seen_chars.update(tuple_item[0])
            seen_second_elements.add(tuple_item[1])
    return result

def correct_unikey(text):
    tokens = text.split()
    for i in range(len(tokens)):
        need_rep = []
        for key, val in map_char.items():
            if val[0] in tokens[i] and val[1] in tokens[i]:
                need_rep.append((val[0], val[1], key))
        need_rep = keep_tuple(need_rep)
        for item in need_rep:
            tokens[i] = tokens[i].replace(item[0], item[2])
            tokens[i] = tokens[i].replace(item[1], "")
    return ' '.join(tokens)
