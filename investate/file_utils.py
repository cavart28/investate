import pickle


def pickle_dump(obj, path):
    with open(path, 'wb') as outfile:
        return pickle.dump(obj, outfile)


def pickle_load(path):
    with open(path, "rb") as pickle_in:
        return pickle.load(pickle_in)
