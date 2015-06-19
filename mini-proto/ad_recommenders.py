__author__ = 'niklas'

import abc
import operator
import adspace

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


class RandomRecommender(AbstractRecommender):

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


class BetaBernoulliModel():
    def __init__(self):
        pass

    def sample_theta(self):
        pass

    def learn_from(self, result):
        pass


class BetaBernoulliThompsonSampler(AbstractRecommender):
    def get_ad(self, context):
        theta_samples = []
        for model in self.beta_bernoulli_models:
            theta_samples.append(model.sample_theta())
        max_index, max_value = max(enumerate(theta_samples), key=operator.itemgetter(1))
        return adspace.ad_from_index(max_index)

    def learn_from(self, context, ad, result):
        model_index = adspace.ad_to_index(ad)
        model = self.beta_bernoulli_models[model_index]
        model.learn_from(result)

    def __init__(self):
        self.beta_bernoulli_models = []
        for i in range(adspace.nr_unique_ads()):
            self.beta_bernoulli_models.append(BetaBernoulliModel())