import time

__author__ = 'niklas'

"""
This is a minimal prototype. Let's see how we can get some data, do stupid recommendations and then send it back
"""

import json
import urllib2
import ad_recommenders
import input_output


class Master():
    """
    This class controls all other moving parts, passing data to where it should be
    """

    def __init__(self):
        pass

    @staticmethod
    def run():
        io = input_output.InputOutput()
        recommender = ad_recommenders.RandomRecommener()

        interaction_range = range(1, int(2e2 + 1))
        run_id_range = range(1, 2)

        for run_id in run_id_range:
            profits = []
            t_run_start = time.clock()
            for interaction_id in interaction_range:
                if interaction_id % 100 == 0:
                    print("Running r_id {}, interaction {}".format(run_id, interaction_id))
                context = io.get_context(run_id, interaction_id)
                ad = recommender.get_ad(context)
                #print("recommend ad: {}".format(ad))
                result = io.get_click(run_id, interaction_id, ad)
                profits.append(ad["price"] * result)
                recommender.learn_from(context, ad, result)
            t_run_end = time.clock()
            total_profits = sum(profits)
            print("interactions: {}, final profit:{}".format(
                interaction_id,
                total_profits
            ))
            print("total time taken for this run: {}s".format(t_run_end - t_run_start))

if __name__ == "__main__":
    master = Master()
    master.run()