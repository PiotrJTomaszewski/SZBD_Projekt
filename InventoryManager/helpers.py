def make_dictionary(names, values):
    dictionary = {}
    dictionary.update(list(zip(names, values)))
    return dictionary


def make_dictionaries_list(names, objects):
    dict_list = [make_dictionary(names, values) for values in objects]
    return dict_list
