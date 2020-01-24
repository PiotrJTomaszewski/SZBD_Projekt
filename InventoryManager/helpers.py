from datetime import date


def make_dictionary(names, values):
    dictionary = {}
    dictionary.update(list(zip(names, values)))
    return dictionary


def make_dictionaries_list(names, objects):
    dict_list = [make_dictionary(names, values) for values in objects]
    return dict_list


def string_to_date(date_as_string):
    return date(int(date_as_string[:4]), int(date_as_string[5:7]), int(date_as_string[8:10]))

