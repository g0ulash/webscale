import json
import urllib2

__author__ = 'niklas'


class NoneCache():

    def __init__(self):
        pass

    def get_context(self, run_id, interaction_id):
        """
        Return cached context, None if not present
        """
        return None

    def set_context(self, run_id, interaction_id, context):
        pass

    def get_click(self, run_id, interaction_id, ad):
        """
        For this interaction, run_id and ad, return how the user reacted earlier. None if unknown
        """
        return None

    def set_user_reaction(self, run_id, interaction_id, reaction):
        pass


class InputOutput():
    """
    Handle interaction with the pseudo-user
    """

    def __init__(self):
        self.teamid = "Smartass1337$$BillYo"
        self.teampw = "12246bef4f7093a8a3d78dff975e180f"
        self.cache = NoneCache()

    def get_context(self, run_id, interaction_id):
        cached = self.cache.get_context(run_id, interaction_id)
        if cached is not None:
            return cached
        source = "http://krabspin.uci.ru.nl/getcontext.json/?i={}&runid={}&teamid={}&teampw={}".format(interaction_id,
                                                                                                       run_id,
                                                                                                       self.teamid,
                                                                                                       self.teampw)
        #print("requesting url: " + source)
        response = json.load(urllib2.urlopen(source))
        context = response["context"]
        #print("received context: {}".format(context))
        self.cache.set_context(run_id, interaction_id, context)
        return context

    def get_user_reaction(self, run_id, interaction_id, ad):
        cached = self.cache.get_click(run_id, interaction_id, ad)
        if cached is not None:
            return cached
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
        #print("requesting url for click: {}".format(url))
        reaction = json.load(urllib2.urlopen(url))
        #print("got response: {}".format(response))
        self.cache.set_user_reaction(run_id, interaction_id, reaction)
        return reaction
