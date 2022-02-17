import hashlib
from pyfiles.config import secret_key


def generate_sign(params):
    """Function to generate sign sha256 HEX
    Params:
        params - list of values"""
    string_to_code = ''
    for par in params:
        string_to_code += str(par) + ':'
    string_to_code = string_to_code[0: -1] + secret_key
    hs = hashlib.sha256(string_to_code.encode('utf-8')).hexdigest()
    return hs


def generate_url(url, params):
    """Function to generate url for another service
    Params:
        url - url of service
        params - dictionary of parameters to pass in url"""
    url_to_return = url + '?'
    for par in params:
        url_to_return += '{}={}&'.format(par, params[par])
    url_to_return = url_to_return[0: -1]
    return url_to_return


def is_digit(string):
    """ Function to check is string a digit
    Inputs string"""
    if string.isdigit():
       return True
    else:
        try:
            float(string)
            return True
        except ValueError:
            return False
