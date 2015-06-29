#! /usr/bin/python2
import os

import time
import json
import urllib2
import datetime
import ad_recommenders
import input_output
import time
import logging
import sys

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
        # logging functions
        li, le, root_logger = Master.set_up_logging()

        # experimental ranges
        interaction_range = list(range(1, int(2e2 + 1)))
        run_id_range = list(range(1, 2))

        # timing bins
        times = {"get_context": [], "get_ad": [], "get_user_reaction": [], "learn_from": []}
        t_ex_start = time.clock()

        li("t_ex_start:{}, first_r_id:{}, last_r_id:{}, n_interactions_per_r_id:{}".format(t_ex_start,
                                                                                           run_id_range[0],
                                                                                           run_id_range[-1],
                                                                                           len(interaction_range)))

        # parts: i/o and the recommender
        io = input_output.InputOutput()
        recommender = ad_recommenders.BetaBinomialThompsonSampler()

        li("recommender module:{}".format(str(recommender)))

        for run_id in run_id_range:
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
            t_run_end = time.clock()
            total_profits = sum(profits)
            print("interactions: {}, final profit:{}".format(
                interaction_id,
                total_profits
            ))
            print("total time taken for this run: {}s".format(t_run_end - t_run_start))
            for key, value in times.iteritems():
                print("timing mean:\t{}\t\t\t{}ms".format(key, sum(value)/len(value) * 1000))

    @staticmethod
    def set_up_logging():
        # get logger + formatter
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        root_logger.setLevel(10)

        # file handler
        log_path = os.path.join(".", "logs")
        t_stamp = str(datetime.datetime.now()).replace(":", "_")
        log_file_path = os.path.join(log_path, "experiment_"+t_stamp+".log")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(log_formatter)
        root_logger.addHandler(file_handler)

        # console handler
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(log_formatter)
        root_logger.addHandler(console_handler)

        # convenience functions
        li = root_logger.info
        le = root_logger.error

        return li, le, root_logger


if __name__ == "__main__":
    master = Master()
    master.run()
