__author__ = 'niklas'

"""
A collection of functions and data related to ads
"""

import random

possible_values = {
    "header": [5, 15, 35],
    "adtype": ["skyscraper", "square", "banner"],
    "color": ["green", "blue", "red", "black", "white"],
    # not range(10, 26) due to bug on teacher side code. keep until further notice
    "productid": list(range(10, 25)),
    # normally: [float(base) + float(decimal)/100 for base in range(0, 25) for decimal in range(0, 100)] + [25]
    # but: same bug, see above. keep until further notice
    "price": list(range(0, 26))
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

