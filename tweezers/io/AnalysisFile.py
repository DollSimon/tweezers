from pathlib import Path
from tweezers.ixo.collections import IndexedOrderedDict, dictStructure
from tweezers.ixo import matfile


class AnalysisFile(IndexedOrderedDict):
    """
    Store analysis results in a Matlab compatible binary format.
    """

    _path = None
    file = None

    def __init__(self, path=None, file=None):
        """
        Constructor for AnalysisFile

        Args:
            path (str): path to the directory containing the file
            file (str): filename that was loaded or that will be saved to
        """
        super().__init__()

        if path:
            self.path = path
        self.file = file

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        try:
            ppath = Path(path)
        except:
            raise ValueError('Invalid path given: {}'.format(path))
        if not ppath.exists():
            raise ValueError('Given path does not exists: {}'.format(path))
        if not ppath.is_dir():
            raise ValueError('Given path is not a directory: {}'.format(path))
        self._path = ppath

    def save(self, keys=None):
        """
        Save analysis file.
        
        Args:
            keys(`list` of `str`): list of keys to write to the file, `None` for all
        """

        toSave = self
        # list of keys to save was given
        if keys:
            toSave = IndexedOrderedDict()
            for key in keys:
                toSave[key] = self[key]
        
        matfile.save(self.path / self.file, toSave)
        
    @classmethod
    def load(cls, file, keys=None):
        """
        Load analysis file from disk.
        
        Args:
            file (str): full path to file to load
            keys(`list` of `str`): list of keys to load from the file (root-level only), `None` for all
           
        Returns:
            :class:`AnalysisFile`
        """

        path = Path(file)
        obj = AnalysisFile(path.parent, path.name)
        data = matfile.load(path,  keys=keys)
        for key, value in data.items():
            obj[key] = value
        return obj

    def structure(self):
        """
        Print the structure of the file, i.e. the contained keys and their type.
        """

        content = dictStructure(self)
        print(content)

    def __str__(self):
        return dictStructure(self)
