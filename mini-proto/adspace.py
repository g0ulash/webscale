import itertools

__author__ = 'niklas'

"""
A collection of functions and data related to ads
"""

import random

possible_values = {
    "header": [5, 15, 35],
    "adtype": ["skyscraper", "square", "banner"],
    "color": ["green", "blue", "red", "black", "white"],
    "productid": list(range(10, 26)),
    # normally: [float(base) + float(decimal)/100 for base in range(0, 25) for decimal in range(0, 100)] + [25]
    # but: same bug, see above. keep until further notice
    "price": list(range(0, 50))
}


def create_random():
    """
    Sample a random ad
    """
    keys = possible_values.keys()
    nr_options_per_key = [len(possible_values[key]) for key in keys]
    random_sample = {}
    for key, nr_options in zip(keys, nr_options_per_key):
        index = random.randint(0, nr_options-1)
        random_sample[key] = possible_values[key][index]
    return random_sample


def roll_adspace_into_list():
    """
    Take all possible combinations of ad-parameters. Put them in a list, in a. order that remains constant.
    :return:
    """
    # sort because keys are not in guaranteed fixed order, which we need
    sorted_keys = sorted(possible_values.keys())
    list_of_value_lists = [possible_values[key] for key in sorted_keys]
    return itertools.product(*list_of_value_lists)

def ad_from_index(index):
    all_ads = roll_adspace_into_list()
    return all_ads[index]
