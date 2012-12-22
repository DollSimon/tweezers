class TweezerExperimentMetaData(dict):
    """
    The metadata of the tweezer experiment.
    """
    def __init__(self):
        dict.__init__(self)
        pass


class TweezerExperiment(object):
    """
    Holds the data and metadata of a tweezer experiment.
    """

    def __init__(self):
        self.metadata = TweezerExperimentMetaData()

