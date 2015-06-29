#! /usr/bin/python2

import time
import json
import urllib2
import ad_recommenders
import input_output
import time
import pymongo

__author__ = 'niklas'

"""
This is a minimal prototype. Let's see how we can get some data, do stupid recommendations and then send it back
"""


class Master():
    """
    This class controls all other moving parts, passing data to where it should be
    """

    def __init__(self):
        pass

    @staticmethod
    def run():
        # db-setup
        client = pymongo.MongoClient()
        db = client["eden"]
        ex_coll = db["snake_experiments"]

        io = input_output.InputOutput()
        recommender = ad_recommenders.BetaBinomialThompsonSampler()
        # recommender_price = ad_recommenders.BootStrapThompson()

        interaction_range = range(1, int(2e2 + 1))
        run_id_range = range(1, 2)

        times = {"get_context": [], "get_ad": [], "get_user_reaction": [], "learn_from": []}
        ex_id = ex_coll.insert({"t_start": time.clock(),
                                    "n_run_ids": len(run_id_range),
                                    "n_interactions_p_rid": len(interaction_range)})
        for run_id in run_id_range:
            ex_coll.update(
                {"_id": ex_id},
                {
                    "$set": {
                        ""
                    }
                }
            )
            profits = []
            t_run_start = time.clock()
            for interaction_id in interaction_range:
                if interaction_id % 100 == 0:
                    print("Running r_id {}, interaction {}".format(run_id, interaction_id))
                s = time.clock()
                context = io.get_context(run_id, interaction_id)
                times["get_context"].append(time.clock() - s)
                s = time.clock()
                ad = recommender.get_ad(context)
                # price = recommender_price.get_ad(context, ad)
                # ad['price'] = price
                times["get_ad"].append(time.clock() - s)
                # print("recommend ad: {}".format(ad))
                s = time.clock()
                user_reaction = io.get_user_reaction(run_id, interaction_id, ad)
                times["get_user_reaction"].append(time.clock() - s)
                # print("user reaction: {}".format(user_reaction))
                profits.append(ad["price"] * user_reaction["effect"]["Success"])
                s = time.clock()
                recommender.learn_from(context, ad, user_reaction)
                # recommender_price.learn_form(context, ad, user_reaction)
                times["learn_from"].append(time.clock() - s)
                ex_coll.update({
                    "_id": ex_id,
                }, {
                    ""
                })
            t_run_end = time.clock()
            total_profits = sum(profits)
            print("interactions: {}, final profit:{}".format(
                interaction_id,
                total_profits
            ))
            print("total time taken for this run: {}s".format(t_run_end - t_run_start))
            for key, value in times.iteritems():
                print("timing mean:\t{}\t\t\t{}ms".format(key, sum(value) / len(value) * 1000))


if __name__ == "__main__":
    master = Master()
    master.run()
