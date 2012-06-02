import string #TODO: find a replacment for this module
import random
import sre_parse

def get_random_string(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    letters, punctuation or space like characters."""
    return "".join([random.choice(string.letters + string.digits + 
            string.punctuation + sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 

def get_random_string_light(desired_length):
    """Returns a random string of length `desired_length` containing digits, 
    some special or space like characters."""
    return "".join([random.choice(string.letters + string.digits + "[]-?+*" + 
            sre_parse.CATEGORY_SPACE) 
        for _ in range(0, desired_length)]) 
