import hashlib
from app.config import secret_key


def generate_sign(params):
    """Function to generate sign sha256 HEX
    Params:
        params: list
            list of values"""
    string_to_code = ''
    for par in params:
        string_to_code += str(par) + ':'
    string_to_code = string_to_code[0: -1] + secret_key
    hs = hashlib.sha256(string_to_code.encode('utf-8')).hexdigest()
    return hs


def generate_url(url, params):
    """Function to generate url for another service
    Params:
        url: str
            url of service
        params: dict
            dictionary of parameters to pass in url"""
    url_to_return = url + '?'
    for par in params:
        url_to_return += '{}={}&'.format(par, params[par])
    url_to_return = url_to_return[0: -1]
    return url_to_return


def generate_list_by_alphabet(params):
    """Function to return list of dictionary values by alphabet order
    Params:
        params: dict
            dictionary of parameters to sort"""
    list_keys = list(params.keys())
    list_keys.sort()
    list_val = [params[key] for key in list_keys]
    return list_val
