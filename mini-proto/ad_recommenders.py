__author__ = 'niklas'

import logging
import abc
import operator
import adspace
import numpy as np
from scipy.optimize import minimize_scalar

logger = logging.getLogger()

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
        logger.info("Sampler initialized. Using "+str(len(self.models))+" models")

    def find_model_for_ad(self, ad):
        for model in self.models:
            if model.ad == ad:
                return model
        raise ValueError


class BootStrapThompson(AbstractRecommender):
    def get_ad(self, context, ad):
        row = np.random.choice(self.betas.shape[0])
        beta = self.betas[row,:]
        result = minimize_scalar(f, args=(context, ad, beta), bounds=(0,50), method="bounded")
        return result.x

    def learn_from(self, context, ad, result):
        for i, val in enumerate(self.params):
            if np.random.binomial(1,.5,1) == 1:
                # Create feature vector from results should be same as in function f
                dummys = product_id_to_dummy(ad)
                age = float(context["Age"])
                price = float(ad["price"])
                y = float(result["effect"]["Success"])
                x = [1, price, price**2, age, age*price, age*price**2, dummys[0]*price, dummys[1]*price, dummys[2]*price, dummys[3]*price, dummys[4]*price, dummys[5]*price, dummys[6]*price, dummys[7]*price, dummys[8]*price, dummys[9]*price, dummys[10]*price, dummys[11]*price, dummys[12]*price, dummys[13]*price, dummys[14]*price, dummys[15]*price]
                x = np.matrix(x).T
                B = np.matrix(self.betas[i,:]).T
                p = 1. / (1. + np.exp(-1*B.T*x))
                B = B + self.alpha*np.float_(y-p)*x - np.insert(self.alpha*2*self.mu*B[1:],0,0)
                self.betas[i,:] = np.array(B.T)[0,:]

    def __init__(self, params, J = 100):
        self.J = J
        self.params = params # OR SET IT OURSELVES
        self.betas = np.zeros([self.J, len(self.params)])
        self.alpha = 0.1
        self.mu = 0.01
        i = 0
        for pars in self.params:
            values = np.random.normal(pars, .1, J)
            self.betas[:,i] = values
            i += 1


def f(x, context, ad, betass):
    # CREATE FEATURE VECTOR FROM CONTEXT AND AD
    # SHOULD BE SAME AS IN LEARN_FROM
    dummys = product_id_to_dummy(ad)
    betass = betass.shape[0]
    feature_vector = [1, x, x**2, context['Age'], context['Age']*x, context['Age']*x**2, dummys[0]*x, dummys[1]*x, dummys[2]*x, dummys[3]*x, dummys[4]*x, dummys[5]*x, dummys[6]*x, dummys[7]*x, dummys[8]*x, dummys[9]*x, dummys[10]*x, dummys[11]*x, dummys[12]*x, dummys[13]*x, dummys[14]*x, dummys[15]*x]
    return -1.*x*(1./(1.*(np.exp(-1*feature_vector*betass))))

def product_id_to_dummy(ad):
    dummys = []
    for i in range(0,16):
        if (ad['productid'] - 10) == i:
            dummys.append(1)
        else:
            dummys.append(0)
    return dummys

class CombineBBBTS(AbstractRecommender):

    def get_ad(self, context):
        ad = self.recommender_bb.get_ad(context)
        price = self.recommender_bts.get_ad(context, ad)
        ad['price'] = price
        return price
	
    def learn_from(self, context, ad, result):
        self.recommender_bts.learn_from(context, ad, result)
        ad.pop("price",None)
        self.recommender_bb.learn_from(context, ad, result)
	
    def __init__(self, params):
        self.recommender_bts = BootStrapThompson(params)
        self.recommender_bb = BetaBinomialThompsonSampler()
        
