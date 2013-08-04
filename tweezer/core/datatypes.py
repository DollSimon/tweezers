import json
import pandas as pd

class TweezerFunction(object):     
    """     
    Abstract class to represent mathematical functions and endow them with 
    user-friendly functionality.
    """
    def __init__(self):
         raise NotImplementedError("Generic Tweezer Function not implemented yet") 

    def __callable__(self):
        raise NotImplementedError("__callable__")
        
    def plot(self):
        raise NotImplementedError("plot method not implemented")


class TweezerDictionary(dict):

    def __init__(self):
        dict.__init__({})

    def dump_to_json(self, file_name):
        """
        Dumps the dictionary to json 

        :param integer new: THis is a test
        :param np.array rocket: The new test type
        

        """
        pass


class TweezerList(list):
    """
    Tweezer List class
    """
    def __init__(self):
        list.__init__([])
        self.test = 4


class TweezerDataFrame(pd.DataFrame):
    """
    Tweezer DataFrame class
    """
    def __init__(self):
        pd.DataFrame.__init__(pd.DataFrame())

    def rocket(self, name):
        print("{} is {}".format(self.new, name))


class Foo(object):

    def __init__(self):
        self.df = pd.DataFrame([1,2,3],[3,4,5])

    def __getattr__(self, attr):
        return getattr(self.df, attr)    

    def __getitem__(self, key):
        ''' Item lookup'''
        return self.df.__getitem__(key)
