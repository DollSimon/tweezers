from pathlib import Path
import json
import re
import pandas as pd
import pickle


def getSubdirs(path):
    """
    Get all subdirectories

    Args:
        path (:class:`pathlib.Path`): path to get subdirectories from

    Returns:
        :class:`list`
    """

    return [x for x in Path(path).iterdir() if x.is_dir()]


class DataFrameJsonEncoder(json.JSONEncoder):
    """
    JSON encoder that allows writing a :class:`pandas.DataFrame` to a JSON file.
    """

    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return {
                "_type": "dataframe",
                "value": obj.to_dict(orient='list')
            }
        return super().default(obj)

    def encode(self, obj):
        jsonStr = super().encode(obj)

        # manipulate to prettify dataframe JSON format
        rxType = re.compile(r'("_type": "dataframe",\s*"value": {\n)(.*?\[\n(.|\n)*?)}')
        rxRepl = re.compile(r'\n\s*(?=(\d|]|-))')
        while True:
            res = rxType.search(jsonStr)
            if not res:
                break
            tmpStr = rxRepl.sub(r' ', res.group(2))
            jsonStr = jsonStr.replace(res.group(2), tmpStr)

        return jsonStr


class DataFrameJsonDecoder(json.JSONDecoder):
    """
    JSON decoder that allows reading a :class:`pandas.DataFrame` from a JSON file.
    """
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if '_type' not in obj:
            return obj
        dtype = obj['_type']
        if dtype == 'dataframe':
            return pd.DataFrame.from_dict(obj['value'], orient='columns')  # pd.read_json(obj['value'])
        return obj


def writePickle(data, path):
    with open(path, 'wb') as fid:
        pickle.dump(data, fid)


def loadPickle(path):
    with open(path, 'rb')as fid:
        data = pickle.load(fid)
    return data
