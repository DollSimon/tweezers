from tweezers.physics.geometry import massSphere
from tweezers.physics.hydrodynamics import dragSphere, diffusionCoefficient
import numpy as np
import pandas as pd


class Sphere:
    """
    Represents a sphere and gives an interface to compute its properties.
    """

    def __init__(self, radius, density=1e-21, viscosity=1e-9, temperature=25):
        """
        Constructor for Sphere

        Args:
            radius (float): Radius of trapped sphere in [nm]. (Default: 1000)
            density (float): Density, ϱ, in [g/nm³]. (Default: 1e-21 g/nm³)
            viscosity (float): Dynamic viscosity in [pN/nm^2 s] (Default: 1e-9 pN/nm^2 s)
            temperature (float): Temperature in [°C]. (Default: 25 °C)
        """

        self.radius = radius
        self.density = density
        self.viscosity = viscosity
        self.temperature = temperature

    def dragCoefficient(self):
        """
        Computes the Stokes drag coefficient in [pN/nm s].
        """

        return dragSphere(self.radius, viscosity=self.viscosity)

    def mass(self):
        """
        Computes the mass of the sphere in [g].
        """

        return massSphere(self.radius, self.density)

    def diffusionCoefficient(self):
        """
        Computes the diffusion coefficient in [nm^2 / s].
        """

        return diffusionCoefficient(radius=self.radius, temperature=self.temperature, viscosity=self.viscosity)


class SingleTrap:
    def __init__(self, stiffness=0.1, obj=Sphere(radius=1000), timeStep=0.001):
        """
        Constructor for SingleTrap

        Args:
            stiffness (float): Stiffness of the trap in [pN/nm] (Default: 0.1 pN/nm)
            obj: an object that provides methods to calculate mass, drag coefficient and diffusion coefficent (e.g.
                :class:`tweezers.simulation.single_trap.Sphere`.
            timeStep (float): Difference between two time points in [s]; delta time (Default: 0.001 s)

        """

        self.stiffness = stiffness
        self.obj = obj
        self.timeStep = timeStep

        self.ev = self.eigenvalues()
        self.c = self.cValues()
        self.A = self.aValues()
        self.alpha = self.alphaValue()
        self.expM = self.exp_matrix()

    def eigenvalues(self):
        """
        Calculates eigenvalues of the Langevin equation in the simulation of OTs according to Norrelykke et al.
        """

        g = self.obj.dragCoefficient()
        m = self.obj.mass()
        k = self.stiffness

        discriminant = np.sqrt((g**2 / (4 * m**2)) - k / m)

        prefactor = g / (2 * m)

        plus = prefactor + discriminant
        minus = prefactor - discriminant

        return {'plus': plus, 'minus': minus}

    def cValues(self):
        """
        Calculates c values in the simulation of OTs according to Norrelykke et al.

        Computes: $c = exp(-λ * ∆t)$
        """

        plus = np.exp(-self.ev['plus'] * self.timeStep)
        minus = np.exp(-self.ev['minus'] * self.timeStep)

        return {'plus': plus, 'minus': minus}

    def aValues(self):
        """
        Calculates A values in the simulation of OTs according to Norrelykke et al.
        """

        l = self.ev
        c = self.c
        D = self.obj.diffusionCoefficient()

        factorA = (l['plus'] + l['minus']) / (l['plus'] - l['minus'])
        factorB = np.sqrt((1 - c['plus']**2) * D / (2 * l['plus']))
        factorC = np.sqrt((1 - c['minus']**2) * D / (2 * l['minus']))

        plus = factorA * factorB
        minus = factorA * factorC

        return {'plus': plus, 'minus': minus}

    def alphaValue(self):
        """
        Calculates alpha in the simulation of OTs according to Norrelykke et al.
        """
        l = self.ev
        c = self.c

        factorA = 2 * np.sqrt(l['plus'] * l['minus']) / (l['plus'] + l['minus'])
        factorB = (1 - c['plus'] * c['minus']) / np.sqrt((1 - c['plus']**2) * (1 - c['minus']**2))

        alphaValue = factorA * factorB

        return alphaValue

    def exp_matrix(self):
        """
        Calculates alpha in the simulation of OTs according to Norrelykke et al.

        Computes: $exp(-M * ∆t)$
        """
        l = self.ev
        c = self.c

        prefactor = 1 / (l['plus'] - l['minus'])

        M = np.matrix(np.zeros((2, 2)))

        M[0, 0] = -l['plus'] * c['minus'] + l['minus'] * c['plus']
        M[0, 1] = -c['plus'] + c['minus']
        M[1, 0] = l['plus'] * l['minus'] * (c['plus'] - c['minus'])
        M[1, 1] = l['plus'] * c['plus'] - l['minus'] * c['minus']

        return prefactor * M

    def step(self):
        """
        Calculates single step in the simulation of OTs according to Norrelykke et al.

        Args:
            eigenvalues (namedtuple): Eigenvalues of Langevin equation; (Fields: 'plus', 'minus')
            aValues (namedtuple): A values in the simulation of an optical trap; (Fields: 'plus', 'minus')
            alpha (float): alpha in the simulation of an optical trap;

        Returns:
            step (np.array): Simulation step; step[0] - deltaX in [nm], step[1] - deltaV in [nm/s]
        """
        l = self.ev
        A = self.A

        v1 = np.array([-1, l['plus']])
        v2 = np.array([1, -l['minus']])

        partA = (A['plus'] * v1 + A['minus'] * v2) * np.sqrt(1 + self.alpha) * np.random.randn()
        partB = (A['plus'] * v1 - A['minus'] * v2) * np.sqrt(1 - self.alpha) * np.random.randn()

        # keep in mind that:
        # deltaX = partA[0] + partB[0]
        # deltaV = partA[1] + partB[1]
        step = partA + partB

        return step

    def simulate(self, datapoints=1e3):
        """
        Simulates the position time series of a sphere in an optical trap

        Args:
            dataPoints (int): Number of data points in final time series. (Default: 1e3)
            timeStep (float): Difference between two time points in [s]; delta time (Default: 0.001 s)
            radius (float): Radius of trapped sphere in [nm]. (Default: 1000)
            viscosity (float): Dynamic viscosity in [pN/nm^2 s] (Default: 1e-9 pN/nm^2 s)
            trapStiffness (float): Stiffness of simulated trap, k, in [pN/nm]. (Default: 0.1 pN/nm)
            temperature (float): Temperature in [°C]. (Default: 25 °C)

        Returns:
            state (pandas.DataFrame): Simulated state of an optical trap. (Columns: 't', 'x', 'v')

        """

        assert self.timeStep > 0
        assert datapoints > 0

        # initialise variables
        state = np.zeros((datapoints, 3))
        state[:, 0] = np.arange(0, self.timeStep * datapoints, self.timeStep)

        # do it
        for i in range(int(datapoints) - 1):
            state[i + 1, 1:3] = state[i, 1:3] * self.expM + self.step()

        #TODO: add time index to pd.DataFrame; makes for easier plotting as time is inherent
        state = pd.DataFrame(state, columns=['t', 'x', 'v'])
        return state