from pathlib import Path
import scipy as sp

from tweezers.ixo.collections import IndexedOrderedDict, dictStructure
from tweezers.ixo import matfile
from tweezers.ixo.fit import PolyFit
from tweezers.ixo.statistics import averageData
import tweezers.io as tio


class TweezersAnalysis(IndexedOrderedDict):
    """
    Store analysis results in a Matlab compatible binary format.
    """

    _path = None
    name = None
    # columns to ignore on baseline correction
    baselineIgnoreColumns = ['BSL', 'bslFlat', 'bslBeads']

    def __init__(self, path=None, name=None):
        """
        Constructor for TweezersAnalysis

        Args:
            path (str): path to the directory containing the file
            name (str): filename that was loaded or that will be saved to
        """
        super().__init__()

        if path:
            self.path = path
        self.name = name

    @classmethod
    def load(cls, file, keys=None):
        """
        Load analysis file from disk.

        Args:
            file (`str` or :class:`pathlib.Path`): full path to file to load
            keys(`list` of `str`): list of keys to load from the file (root-level only), `None` for all

        Returns:
            :class:`TweezersAnalysis`
        """

        path = Path(file)
        obj = TweezersAnalysis(path.parent, path.name)
        data = matfile.load(path, keys=keys)
        for key, value in data.items():
            obj[key] = value
        return obj

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
        Save analysis file to the path and name it was created with.
        
        Args:
            keys(`list` of `str`): list of keys to write to the file, `None` for all
        """

        toSave = self
        # list of keys to save was given
        if keys:
            toSave = IndexedOrderedDict()
            for key in keys:
                toSave[key] = self[key]
        
        matfile.save(self.path / self.getFilename(self.name), toSave)

    def structure(self):
        """
        Print the structure of the file, i.e. the contained keys and their type.
        """

        content = dictStructure(self)
        print(content)

    def __str__(self):
        return dictStructure(self)

    def __repr__(self):
        return self.name

    def _repr_pretty_(self, p, cycle):
        """
        Pretty printer used by IPython (and Jupyter notebook).
        """

        p.text(self.name)
        p.break_()
        super()._repr_pretty_(p, cycle)

    @staticmethod
    def isAnalysisFile(file):
        """
        Check if the provided file is a valid analysis file.

        Args:
            file (`str` or :class:`pathlib.Path`): path to the file to check

        Returns:
            bool
        """

        _file = Path(file)
        if not (_file.exists() and _file.is_file()):
            return False
        if not _file.name.endswith('.h5'):
            return False
        return True

    @staticmethod
    def getFilename(identifier):
        """
        Create a filename from the given identifier.

        Args:
            identifier (str): identifier to use for the filename

        Returns:
            str
        """

        keepcharacters = ('_', '-', ' ', '.')
        res = "".join(c for c in identifier if c.isalnum() or c in keepcharacters)
        if not res.endswith('.h5'):
            res += '.h5'
        return res
