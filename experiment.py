# -*- coding: utf-8 -*-
from db.database import Database
from db.advicelog import Advice

class Experiment():
    
    def __init__(self, exp_id, key):
        self.db = Database()
        self.advice_db = Advice()
        self.exp_id = exp_id   # sets the experimentID
        self.properties = self.db.get_one_experiment(self.exp_id)
        self.key = key
        self.valid = False     # should be taken from Redis
        self.log_advice_bool = (self.properties['adviceID'] == 'true')    # should be taken from Redis
    
    def is_valid(self):
        """Checks wheter the exp_id and key match for the current experiment.
        
        Input arguments:
        none
            
        Returns:
        A boolean: true if a valid key is provided, false otherwise.
        """
        # After database has a decent is_valid function, change to self.db.is_valid(exp_id)
        self.valid = True
        return self.valid
    
    def advice(self):
        return self.log_advice_bool
        
    def gen_advice_id(self, context, action):
        return self.advice_db.log_advice(context, action)
        
    def get_by_advice_id(self, _id):
        return self.advice_db.get_advice(_id)
    
    ### THESE NEED CHANGING FOR THE NEW LOCATION
    def run_action_code(self, context, action):    #or make it get_action_code and return the code instead
        self.action = action
        self.context = context
        code = self.db.experiment_properties("exp:%s:properties" % (self.exp_id), "getAction")
        exec(code)
        return self.action
        
    def run_reward_code(self, context):
        self.context = context
        code = self.db.experiment_properties("exp:%s:properties" % (self.exp_id), "setReward")
        exec(code)
        return True
    ### END OF CHANGE
        
    def set_theta(self, values, context = None, action=None, all_action=False, all_context=False, name="theta"):
        key = "exp:%s:" % (self.exp_id) +name
        return self.db.set_theta(values, key, context, action, all_action, all_context)
    
    def get_theta(self, context = None, action=None, all_action=False, all_context=False, all_float=True, name="theta"):
        key = "exp:%s:" % (self.exp_id) +name    
        return self.db.get_theta(key, context, action, all_action, all_context, all_float)
    
    
