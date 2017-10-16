from pathlib import Path
from tweezers.ixo.collections import IndexedOrderedDict
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
            path=None, file=None
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

    def save(self):
        """
        Save analysis file.
        
        Args:
            
           
        Returns:
            
        """
        
        matfile.save(self.path / self.file, self)
        
    @classmethod
    def load(cls, path, file):
        """
        Load analysis file from disk.
        
        Args:
            cls, path, file
           
        Returns:
            :class:`AnalysisFile`
        """
        
        obj = AnalysisFile(path, file)
        data = matfile.load(obj.path / obj.file)
        for key, value in data.items():
            obj[key] = value
        return obj
