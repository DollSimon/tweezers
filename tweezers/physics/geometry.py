import numpy as np


def volumeSphere(radius=1000):
    """
    Volume of a sphere

    Args:
        radius (float): Radius (Default: 1000)

    Returns:
        volume (float): Volume in [input units³]
    """
    assert radius > 0

    volume = 4 / 3 * np.pi * radius**3

    return volume


def massSphere(radius=1000, density=1e-21,
                verbose=False, inferDensity=True):
    """
    Calculates mass of a sphere

    Args:
        radius (float): Radius in [nm]. (Default: 1000 nm)
        density (float): Density, ϱ, in [g/nm³]. (Default: 1e-21 g/nm³)
        verbose (bool): Flag whether to show extra information. (Default: False)
        inferDensity (bool): If true inputs above 1e-5 are interpreted as g/cm³. (Default: True)

    Returns:
        mass (float):  Mass in [g]
    """
    assert radius > 0
    assert density > 0

    volume = volumeSphere(radius=radius)

    # check if density is provided in g/cm³.
    if inferDensity and density > 1e-5:
        print("Assuming that ϱ was provided in [g/cm³]. Converting to g/nm³")
        density /= 1e21
        print("ϱ is now: {} g/nm³".format(density))

    mass = volume * density

    if verbose:
        print("Input:")
        print("Radius of Sphere [nm]: {}".format(radius))
        print("Density of material [g/nm³]: {} \n".format(density))

        print("Output:")
        print("Mass of sphere [g]: {}\n".format(mass))

    return mass