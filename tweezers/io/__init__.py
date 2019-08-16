from collections import OrderedDict

from .BaseSource import BaseSource
from .TxtBiotecSource import TxtBiotecSource
from .TxtMpiSource import TxtMpiSource
from .TdmsCTrapSource import TdmsCTrapSource
from .Hdf5BiotecSource import Hdf5BiotecSource

SOURCE_CLASSES = OrderedDict([
            ('TxtBiotecSource', TxtBiotecSource),
            ('Hdf5BiotecSource', Hdf5BiotecSource),
            ('TdmsCTrapSource', TdmsCTrapSource),
            ('TxtMpiSource', TxtMpiSource)
        ])
