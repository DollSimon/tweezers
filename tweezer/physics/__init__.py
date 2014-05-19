__doc__ = """\
Module with general physical and chemical functions
"""

import os
import glob

SOURCE_FILES = glob.glob(os.path.dirname(__file__) + "/*.py")
__all__ = [os.path.basename(f)[: -3] for f in SOURCE_FILES]

# imports
from .thermodynamics import thermal_energy

from .hydrodynamics import drag_on_sphere

from .viscosity import (dynamic_viscosity_of_mixture,
                        water_dynamic_viscosity,
                        water_density,
                        glycerol_dynamic_viscosity,
                        glycerol_density)

from .constants import (kB, h, NA, c, vacuumPermittivity)