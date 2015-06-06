__author__ = 'niklas'

"""
This is a minimal prototype. Let's see how we can get some data, do stupid recommendations and then send it back
"""

import json
import urllib2
import ad_recommenders


class InputOutput():
    """
    Handle interaction with the pseudo-user
    """

    def __init__(self):
        self.teamid = "Smartass1337$$BillYo"
        self.teampw = "12246bef4f7093a8a3d78dff975e180f"

    def get_context(self, run_id, interaction_id):
        source = "http://krabspin.uci.ru.nl/getcontext.json/?i={}&runid={}&teamid={}&teampw={}".format(interaction_id,
                                                                                                       run_id,
                                                                                                       self.teamid,
                                                                                                       self.teampw)
        print("requesting url: " + source)
        response = json.load(urllib2.urlopen(source))
        context = response["context"]
        print("received context: {}".format(context))
        return context

    def get_click(self, run_id, interaction_id, ad):
        url = "http://krabspin.uci.ru.nl/proposePage.json/?i={}&runid={}&teamid={}&header={}&adtype={}&color={}&productid={}&price={}&teampw={}".format(
            interaction_id,
            run_id,
            self.teamid,
            ad["header"],
            ad["adtype"],
            ad["color"],
            ad["productid"],
            ad["price"],
            self.teampw)
        print("requesting url for click: {}".format(url))
        response = json.load(urllib2.urlopen(url))
        print("got response: {}".format(response))
        click = response["effect"]["Success"]
        return click




class Master():
    """
    This class controls all other moving parts, passing data to where it should be
    """

    def __init__(self):
        pass

    @staticmethod
    def run():
        io = InputOutput()
        recommender = ad_recommenders.Satan()

        interaction_range = range(1, int(10e5 + 1))
        run_id_range = range(1, 2)

        for run_id in run_id_range:
            for interaction_id in interaction_range:
                context = io.get_context(run_id, interaction_id)
                ad = recommender.get_ad(context)
                print("recommend ad: {}".format(ad))
                result = io.get_click(run_id, interaction_id, ad)
                recommender.learn_from(context, ad, result)


if __name__ == "__main__":
    master = Master()
    master.run()