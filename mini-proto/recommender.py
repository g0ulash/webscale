__author__ = 'niklas'

import abc

class AbstractRecommender():
    """
    Inherit from this class and implement the get_ad() and learn_from() methods to adhere to the recommender
    interface
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_ad(self, context):
        """
        Given the current state of the recommender and the current context, recommend an ad
        """
        pass

    @abc.abstractmethod
    def learn_from(self, context, ad, result):
        """
        For a tuple (context, ad, received reward) adapt internal parameters to make a better recommendation
        next time
        """
        pass


class RandomRecommener(AbstractRecommender):

    def __init__(self):
        pass

    def get_ad(self, context):
        import adspace
        return adspace.create_random()

    def learn_from(self, context, ad, result):
        pass


class Satan(AbstractRecommender):
    """
    Tempt user (by constantly recommending the same ad)
    """

    def __init__(self):
        pass

    def get_ad(self, context):
        ad = {
            "header": 15,
            "adtype": "skyscraper",
            "color": "white",
            "productid": 17,
            "price": 25.0
        }
        return ad

    def learn_from(self, context, ad, result):
        # Satan does not learn
        pass
