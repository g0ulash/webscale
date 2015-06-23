__author__ = 'niklas'

import abc
import operator
import adspace
import numpy as np

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


class BetaBinomialModel():

    def __init__(self, ad):
        self.ad = ad
        self.params = {"alpha": 1.0,
                       "beta": 1.0}

    def estimate_reward(self):
        """
        Assume: Next reward = Single draw from Bernoulli with Theta parameter drawn from Beta distribution.
        In this case: Theta is directly the expected value. So we just return the value from the Beta draw.
        :return: estimated reward (0 till 1)
        """
        reward = np.random.beta(self.params["alpha"], self.params["beta"])
        # print("estimated reward: "+str(reward))
        return reward

    def learn_from(self, result):
        """
         When this function is called it means that the arm belonging to this model has been played
         We need to update the alpha+beta parameters of our Beta posterior
         According to what I have found:
         alpha = alpha + result
         beta = beta + 1 - result
        :param result: weird JSON result, 0 or 1 (no click / click) is buried in there
        :return:
        """
        result = result["effect"]["Success"]
        self.params["alpha"] += result
        self.params["beta"] += 1 - result
        # print("Updated beta params")


class BetaBinomialThompsonSampler(AbstractRecommender):
    def get_ad(self, context):
        max_estimated_reward = None
        best_model = None
        for model in self.models:
            estimated_reward = model.estimate_reward()
            if max_estimated_reward is None or estimated_reward > max_estimated_reward:
                best_model = model
                max_estimated_reward = estimated_reward
        return best_model.ad

    def learn_from(self, context, ad, result):
        model = self.find_model_for_ad(ad)
        model.learn_from(result)

    def __init__(self):
        self.models = []
        all_ads = adspace.roll_adspace_into_list()
        for ad in all_ads:
            self.models.append(BetaBinomialModel(ad))
        print("Sampler initialized. Using "+str(len(self.models))+" models")

    def find_model_for_ad(self, ad):
        for model in self.models:
            if model.ad == ad:
                return model
        raise ValueError
