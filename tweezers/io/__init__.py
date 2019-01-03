from collections import OrderedDict

from .BaseSource import BaseSource
from .TxtBiotecSource import TxtBiotecSource
from .TxtMpiSource import TxtMpiSource
from .TdmsCTrapSource import TdmsCTrapSource

SOURCE_CLASSES = OrderedDict([
            ('TxtBiotecSource', TxtBiotecSource),
            ('TdmsCTrapSource', TdmsCTrapSource),
            ('TxtMpiSource', TxtMpiSource)
        ])
