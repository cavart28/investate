"""A few simple functions to handle files"""

import pickle


def pickle_dump(obj, path):
    """
    Dump a pickle
    """
    with open(path, 'wb') as outfile:
        return pickle.dump(obj, outfile)


def pickle_load(path):
    """
    Load a pickle
    """
    with open(path, 'rb') as pickle_in:
        return pickle.load(pickle_in)
