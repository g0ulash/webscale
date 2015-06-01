__author__ = 'niklas'

"""
This is a minimal prototype. Let's see how we can get some data, do stupid recommendations and then send it back
"""


class InputOutput():
    """
    Handle interaction with the pseudo-user
    """

    def __init__(self):
        pass

    def get_context(self, run_id, interaction_id):
        raise NotImplementedError
        return context

    def get_click(self, run_id, interaction_id, ad):
        raise NotImplementedError
        return click


class Satan():
    """
    Tempt user
    """

    def __init__(self):
        pass

    def get_ad(self, context):
        raise NotImplementedError
        return ad

    def learn_from(self, context, ad, result):
        # Satan does not learn
        pass


class Master():
    """
    This class controls all other moving parts, passing data to where it should be
    """

    def __init__(self):
        pass

    @staticmethod
    def run():
        io = InputOutput()
        recommender = Satan()

        interaction_range = range(start=1, stop=10e5+1)
        run_id_range = range(start=1, stop=2)

        for run_id in run_id_range:
            for interaction_id in interaction_range:
                context = io.get_context(run_id, interaction_id)
                ad = recommender.get_ad(context)
                result = io.get_click(run_id, interaction_id, ad)
                recommender.learn_from(context, ad, result)



if __name__ == "__main__":
    master = Master()
    master.run()