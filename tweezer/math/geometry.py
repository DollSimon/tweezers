__doc__ = """\
Geometry module with useful classes and functions.
"""

import numpy as np


class Point(object):
    """Basic point class"""
    def __init__(self, *args, **kwargs):
        if kwargs:

            if 'x' in kwargs:
                self.x = kwargs['x']
            else:
                self.x = 0

            if 'y' in kwargs:
                self.y = kwargs['y']
            else:
                self.y = 0

            if 'z' in kwargs:
                self.z = kwargs['z']
            else:
                self.z = 0

        elif np.iterable(args[0]):
            coords = args[0]
            if len(coords) == 3:
                self.x = coords[0]
                self.y = coords[1]
                self.z = coords[2]
            elif len(coords) == 2:
                self.x = coords[0]
                self.y = coords[1]
                self.z = 0

        else:
            if len(args) == 3:
                self.x = args[0]
                self.y = args[1]
                self.z = args[2]
            elif len(args) == 2:
                self.x = args[0]
                self.y = args[1]
                self.z = 0
            elif len(args) == 1 and not isinstance(args, list):
                self.x = args[0]
                self.y = 0
                self.z = 0

    def __repr__(self):
        return 'Point({0.x!r}, {0.y!r}, {0.z!r})'.format(self)

    def __str__(self):
        return '({0.x!s}, {0.y!s}, {0.z!s})'.format(self)

    @classmethod
    def origin(cls):
        """
        Alternative constructor for origin
        """
        return cls(0, 0, 0)

    @property
    def distanceToOrigin(self):
        """
        Euclidean Norm.
        """
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    @property
    def coordinates(self):
        """
        Coordinates of point as list

        Returns:
            (list): 3D coordinates
        """
        return [self.x, self.y, self.z]

    def __add__(self, other):
        """
        Adding two Points together by adding their coordinates.
        """
        if isinstance(other, Point):
            coordinates = [x + y for x, y in zip(self.coordinates, other.coordinates)]
            return Point(coordinates)
        else:
            raise ValueError('Cannot add non-Point, {}, to a Point'.format(other))

    def __radd__(self, other):
        """
        Adding a number to a point acts like a translation.
        """
        if isinstance(other, Point):
            coordinates = [x + y for x, y in zip(self.coordinates, other.coordinates)]
            return Point(coordinates)
        else:
            coordinates = [other + x for x in self.coordinates]
            return Point(coordinates)

    def __sub__(self, other):
        """
        Subtract a Point from another Point by subtracting their coordinates.
        """
        if isinstance(other, Point):
            coordinates = [x - y for x, y in zip(self.coordinates, other.coordinates)]
            return Point(coordinates)
        else:
            raise ValueError('Cannot subtract non-Point, {}, from a Point'.format(other))

    def __mul__(self, factor):
        """Multiply a Point's coordinates by a factor."""
        return Point([x * factor for x in self.coordinates])

    def __rmul__(self, factor):
        """Multiply a Point's coordinates by a factor."""
        return Point([x * factor for x in self.coordinates])

    def __truediv__(self, factor):
        """Divide a Point's coordinates by a factor."""
        return Point([x / factor for x in self.coordinates])

    def __len__(self):
        return 3

    def __iter__(self):
        return iter(self.coordinates)


class Vector(object):
    """
    Basic Vector class.
    """
    def __init__(self, start=Point(0, 0, 0), end=Point(1, 1, 1)):
        self.start = start
        self.end = end
        self.x = end.x - start.x
        self.y = end.y - start.y
        self.z = end.z - start.z

    @property
    def length(self):
        """
        Length of the vector defined as L^2 norm.
        """
        return np.linalg.norm([self.x, self.y, self.z])

    @property
    def direction(self):
        pass

    @property
    def coordinates(self):
        """
        Coordinates of vector as list. The vector coordinates are independent from the anchor points of the vector.

        The coordinates coincide with the end point only if the start point is the origin (0, 0, 0).

        Returns:
            (list): 3D coordinates
        """
        return [self.x, self.y, self.z]

    def norm(self, order=None):
        """
        General norm of the vector.

        Args:
            order (optional, non-zero int): order of the norm
        """
        return np.linalg.norm([self.x, self.y, self.z], ord=order)

    def inner(self, other):
        """
        Inner product between two vectors

        :param other: Vector
        :return: inner Inner Product
        """
        if isinstance(other, Vector):
            inner = sum(x * y for x, y in zip(self.coordinates, other.coordinates))
            return inner
        else:
            raise ValueError('Cannot calculate the inner product between non-Vector, {}, and a Vector'.format(other))

    def angleTo(self, other, inDegrees=False):
        """
        Calculates the angle between two vectors.
        """
        if isinstance(other, Vector):
            angle = np.arccos(self.inner(other) / (self.norm() * other.norm()))

            if inDegrees:
                angle = 180 * angle / np.pi
            return angle
        else:
            raise ValueError('Cannot calculate the angle between non-Vector, {}, and a Vector'.format(other))


    def __neg__(self):
        """
        Negation of a vector changes its direction.
        """
        return Vector(start=self.end, end=self.start)

    def __add__(self, other):
        """
        Adding one vector to another.
        """
        if isinstance(other, Vector):
            coords = [x + y for x, y in zip(self.coordinates, other.coordinates)]
            return Vector(end=Point(coords[0], coords[1], coords[2]))
        else:
            raise ValueError('Cannot add non-Vector, {}, to a Vector'.format(other))

    def __sub__(self, other):
        """
        Subtracting one vector from the other.
        """
        if isinstance(other, Vector):
            coords = [x - y for x, y in zip(self.coordinates, other.coordinates)]
            return Vector(end=Point(coords[0], coords[1], coords[2]))
        else:
            raise ValueError('Cannot subtract non-Vector, {}, from a Vector'.format(other))

    def __iter__(self):
        return iter(self.coordinates)


class UnitVector(Vector):
    """
    Basic UnitVector class.
    """
    def __init__(self, v=Vector()):
        self.start = v.start
        self.end = v.end - v.start


class Line(object):
    """
    Basic Line class.
    """
    pass


class Plane():
    """
    Basic Plane class.
    """
    pass
