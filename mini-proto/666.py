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
    def run(rid_start, rid_end, iid_start, iid_end, recommender):
        # set up logging
        root_logger = logging.getLogger()
        # convenience functions
        li = root_logger.info
        le = root_logger.error
        ld = root_logger.debug

        # experimental ranges
        run_id_range = list(range(rid_start, rid_end))
        interaction_range = list(range(iid_start, iid_end))

        # timing bins
        times = {"get_context": [], "get_ad": [], "get_user_reaction": [], "learn_from": []}
        t_ex_start = time.clock()

        li("t_ex_start:{}, first_r_id:{}, last_r_id:{}, n_interactions_per_r_id:{}".format(t_ex_start,
                                                                                           run_id_range[0],
                                                                                           run_id_range[-1],
                                                                                           len(interaction_range)))

        # parts: i/o
        io = input_output.InputOutput()

        li("recommender module:{}".format(str(recommender)))

        # variables valid for all of the experiment
        global_profits = []
        global_times = []
        errors = 0

        for run_id in run_id_range:
            profits = []
            t_run_start = time.clock()
            li("Starting r_id:{}".format(run_id))
            for interaction_id in interaction_range:
                # every 100 interactions: log message visible on terminal
                if interaction_id % 100 == 0:
                    lf = li
                else:
                    lf = ld
                lf("Running r_id {}, interaction {}".format(run_id, interaction_id))

                # get context
                s = time.clock()
                try:
                    context = io.get_context(run_id, interaction_id)
                except urllib2.URLError:
                    le("Error while getting the context, skipping to next")
                    errors += 1
                    continue
                times["get_context"].append(time.clock() - s)
                ld("context received:{}".format(context))

                # get recommendation
                s = time.clock()
                ad = recommender.get_ad(context)
                times["get_ad"].append(time.clock() - s)
                ld("recommend ad:{}".format(ad))

                # get user reaction
                s = time.clock()
                try:
                    user_reaction = io.get_user_reaction(run_id, interaction_id, ad)
                except urllib2.URLError:
                    le("Error while getting the user reaction, skipping to next")
                    errors += 1
                    continue
                times["get_user_reaction"].append(time.clock() - s)
                ld("user reaction:{}".format(user_reaction))

                profits.append(ad["price"] * user_reaction["effect"]["Success"])

                # update models
                s = time.clock()
                recommender.learn_from(context, ad, user_reaction)
                times["learn_from"].append(time.clock() - s)

            # bookkeeping after run
            t_run_end = time.clock()
            total_profits = sum(profits)
            t_total_run = t_run_end - t_run_start
            global_profits.append(total_profits)
            global_times.append(t_total_run)

            # logging after run finishes
            li("finished r_id:{}".format(run_id))
            li("total time taken for this run:{}s".format(t_total_run))
            li("total profit for this run:{}".format(total_profits))
            li("timings:")
            for key, value in times.iteritems():
                li("timing mean:\t{}\t\t\t{}ms".format(key, sum(value) / len(value) * 1000))

        # bookkeeping after experiment
        t_ex_end = time.clock()
        t_ex_total = t_ex_end - t_ex_start

        ex_total_profit = sum(global_profits)
        ex_mean_profit = float(ex_total_profit) / len(global_profits)

        ex_mean_time = float(sum(global_times)) / len(global_times)

        # logging after experiment
        li("finished this experiment")

        li("Errors encountered:{}".format(errors))

        li("total time taken:{}".format(t_ex_total))
        li("mean time taken per run:{}".format(ex_mean_time))
        li("standard error of time per run:{}".format("???"))

        li("total profit:{} Galactic Credits".format(ex_total_profit))
        li("mean profit:{} Galactic Credits".format(ex_mean_profit))
        li("standard error of mean profit per run:{}".format("???"))

        li("This is a triumph")


class LogAdmin():

    def __init__(self):
        self.root_logger = None
        self.log_formatter = None
        self.file_handler = None
        self.console_handler = None

    def set_up_logging(self):
        # get logger + formatter
        log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        root_logger = logging.getLogger()
        root_logger.setLevel(10)
        self.log_formatter = log_formatter
        self.root_logger = root_logger

        # file handler
        self.attach_new_log_file()

        # console handler
        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(20)
        root_logger.addHandler(console_handler)
        self.console_handler = console_handler

        return root_logger

    def attach_new_log_file(self):
        if self.file_handler is not None:
            self.root_logger.removeHandler(self.file_handler)
            self.file_handler = None
        log_path = os.path.join(".", "logs")
        t_stamp = str(datetime.datetime.now()).replace(":", "_")
        log_file_path = os.path.join(log_path, "experiment_" + t_stamp + ".log")
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(self.log_formatter)
        self.root_logger.addHandler(file_handler)
        self.file_handler = file_handler


if __name__ == "__main__":
    la = LogAdmin()
    rl = la.set_up_logging()
    master = Master()
    master.run(rid_start=1, rid_end=50, iid_start=1, iid_end=int(1e5 + 1),
               recommender=ad_recommenders.CombineBBBTS([-1, 0.5, 0.005, 0.5, 0.005, 0.005, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025]))
    # Run this one for test set!  
    #master.run(rid_start=10001, rid_end=10050, iid_start=1, iid_end=int(1e5 + 1), recommender=ad_recommenders.CombineBBBTS([-1, 0.5, 0.005, 0.5, 0.005, 0.005, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025, 0.025]))
               
