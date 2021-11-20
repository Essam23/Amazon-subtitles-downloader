import re


def sort_urls(url_list,reverse=True):
    return sorted(url_list, key=lambda k: k['bandwidth'], reverse=reverse)


def name_checker(name):
    name = name.replace("'", "")
    name = re.findall(r"([\w\d-]+)", name)
    return ' '.join([x for x in name])
