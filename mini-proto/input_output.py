import copy
import json
import os
import urllib2
import abc
from abc import abstractmethod
import sqlite3
import logging

__author__ = 'niklas'



class AbstractCache():
    """
    This defines the caching interface
    """
    __metaclass__ = abc.ABCMeta

    @abstractmethod
    def get_context(self, run_id, interaction_id):
        """
        Return cached context, None if not present
        """
        pass

    @abstractmethod
    def set_context(self, run_id, interaction_id, context):
        pass

    @abstractmethod
    def get_click(self, run_id, interaction_id, ad):
        """
        For this interaction, run_id and ad, return how the user reacted earlier. None if unknown
        """
        pass

    @abstractmethod
    def set_user_reaction(self, run_id, interaction_id, reaction):
        pass


class NoneCache(AbstractCache):
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


class SQLiteCache(AbstractCache):
    """2015-06-30 00:01:30,461 [MainThread  ] [INFO ]  context received:
    {u'Referer': u'NA', u'Age': 43.0, u'Language': u'EN', u'ID': 3493, u'Agent': u'OSX'}"""

    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(".", "cache", "sqlite-cache.db"))
        self.context_keys = sorted(["Referer", "Age", "Language", "ID", "Agent"])

        columns = "(run_id integer, interaction_id integer, Age integer, Agent text, ID integer, Language text, Referer text)"
        q = "CREATE TABLE IF NOT EXISTS contexts {}".format(columns)
        self.conn.execute(q)
        logging.getLogger().info("SQLite cache set up")

    def set_context(self, run_id, interaction_id, context):
        cc = copy.copy(context)
        cc["run_id"] = run_id
        cc["interaction_id"] = interaction_id
        q = "INSERT INTO contexts VALUES (:run_id,:interaction_id,:Age,:Agent,:ID,:Language,:Referer)"
        self.conn.execute(q, cc)
        self.conn.commit()
        logging.getLogger().debug("Context written to SQLite cache")

    def get_context(self, run_id, interaction_id):
        cursor = self.conn.execute("SELECT * FROM contexts WHERE run_id=:run_id AND interaction_id=:interaction_id",
                                   {"run_id": run_id,
                                    "interaction_id": interaction_id})
        context = cursor.fetchone()
        if context is not None:
            logging.getLogger().debug("Cache hit for context")
        else:
            logging.getLogger().debug("Cache miss for context")
        return context

    def get_click(self, run_id, interaction_id, ad):
        pass

    def set_user_reaction(self, run_id, interaction_id, reaction):
        pass


class InputOutput():
    """
    Handle interaction with the pseudo-user
    """

    def __init__(self):
        self.teamid = "Smartass1337$$BillYo"
        self.teampw = "12246bef4f7093a8a3d78dff975e180f"
        self.cache = SQLiteCache()

    def get_context(self, run_id, interaction_id):
        cached = self.cache.get_context(run_id, interaction_id)
        if cached is not None:
            return cached
        source = "http://krabspin.uci.ru.nl/getcontext.json/?i={}&runid={}&teamid={}&teampw={}".format(interaction_id,
                                                                                                       run_id,
                                                                                                       self.teamid,
                                                                                                       self.teampw)
        # print("requesting url: " + source)
        response = json.load(urllib2.urlopen(source))
        context = response["context"]
        # print("received context: {}".format(context))
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
        # print("requesting url for click: {}".format(url))
        reaction = json.load(urllib2.urlopen(url))
        # print("got response: {}".format(response))
        self.cache.set_user_reaction(run_id, interaction_id, reaction)
        return reaction
