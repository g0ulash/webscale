__author__ = 'niklas'


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
        #print("requesting url: " + source)
        response = json.load(urllib2.urlopen(source))
        context = response["context"]
        #print("received context: {}".format(context))
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
        #print("requesting url for click: {}".format(url))
        response = json.load(urllib2.urlopen(url))
        #print("got response: {}".format(response))
        click = response["effect"]["Success"]
        return click
