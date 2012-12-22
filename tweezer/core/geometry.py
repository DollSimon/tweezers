"""
Geometry classes and functions
"""


from math import sqrt
import numpy as np
from numpy.linalg import norm

# Matplotlib imports
import matplotlib as mpl
import mpl_toolkits.mplot3d as m3d
import matplotlib.pyplot as plt


class Point(object):

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.coordinates = np.asarray([x, y, z])
        self.distance_to_origin = np.linalg.norm(self.coordinates)

    def __str__(self):
        s = """ Point coordinates: \n
        x = {}\
        y = {}\
        z = {}\
        """.format(self.x, self.y, self.z)
        return s

    def draw(self):
        """
        Plot Point in 3D
        """
        x = np.array([self.x])
        y = np.array([self.y])
        z = np.array([self.z])

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot(x, y, z, 'o')

        # get projection
        # cset = ax.contour(x, y, z, zdir='y', offset=40, cmap=cm.coolwarm)

        # Get labels
        ax.set_xlabel('X')
        ax.set_xlim(self.x - 5, self.x + 5)
        ax.set_ylabel('Y')
        ax.set_ylim(self.y - 5, self.y + 5)
        ax.set_zlabel('Z')
        ax.set_zlim(self.z - 5, self.z + 5)

        plt.show()

    @staticmethod
    def draw_example():
        mpl.rcParams['legend.fontsize'] = 10

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
        z = np.linspace(-2, 2, 100)
        r = z ** 2 + 1
        x = r * np.sin(theta)
        y = r * np.cos(theta)
        ax.plot(x, y, z, label='parametric curve')
        ax.legend()

        plt.show()


class Line(object):
    """
    Line constructed from 2 points in 3D
    """

    def __init__(self, first_anchor_point, second_anchor_point):
        if (isinstance(first_anchor_point, np.ndarray) or isinstance(first_anchor_point, list)) and \
           (isinstance(second_anchor_point, np.ndarray) or isinstance(first_anchor_point, list)):
            self.anchor_a = np.asarray(first_anchor_point)
            self.anchor_b = np.asarray(second_anchor_point)
        else:
            raise ValueError("Anchor points should be Numpy ndarrays or lists.")

    @property
    def normalised_direction(self):
        return (self.anchor_b - self.anchor_a) /\
            norm(self.anchor_b - self.anchor_a)

    def __str__(self):
        p = self.anchor_a
        q = self.anchor_b

        s = """ Line constructed from two points: \n
        P = [{}, {}, {}]\n
        Q = [{}, {}, {}]\n
        """.format(p[0], p[1], p[2], q[0], q[1], q[2])
        return s

    def normal_form(self):
        pass

    def draw(self):
        """
        Plot Line in 3D
        """
        p = self.anchor_a
        v  = self.normalised_direction

        # alpha = np.zeros(100)

        # for col in range(100):
        #     alpha[:, col] = np.linspace(-0.5, 1.5, 100)

        # line = np.add(p, np.multiply(alpha, v))

        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.scatter3D(*zip(p, p + v))
        # ax.plot(line[0], line[1], line[2])

        # get projection
        # cset = ax.contour(x, y, z, zdir='y', offset=40, cmap=cm.coolwarm)

        # Get labels
        ax.set_xlabel('X')
        ax.set_xlim(min(line[0]) - 5, max(line[0]) + 5)
        ax.set_ylabel('Y')
        ax.set_ylim(min(line[1]) - 5, max(line[1]) + 5)
        ax.set_zlabel('Z')
        ax.set_zlim(min(line[2]) - 5, max(line[2]) + 5)

        plt.show()


class Plane(object):
    """
    Plane constructed from 3 anchor points
    """

    def __init__(self, first_anchor_point,
                 second_anchor_point, third_anchor_point):
        self.anchor_a = first_anchor_point
        self.anchor_b = second_anchor_point
        self.anchor_c = third_anchor_point

        # self.a = np.array([[1, 2], [3, 4]]
        # self.c1 = np.linalg.det(self.a)

    @staticmethod
    def draw_example():
        point = np.array([1, 2, 3])
        normal = np.array([1, 1, 2])

        # a plane is a*x+b*y+c*z+d=0
        # [a,b,c] is the normal. Thus, we have to calculate
        # d and we're set
        d = - np.sum(point * normal)  # dot product

        # create x,y
        xx, yy = np.meshgrid(range(100), range(100))

        # calculate corresponding z
        z = (- normal[0] * xx - normal[1] * yy - d) / normal[2]

        # plot the surface
        plt3d = plt.figure().gca(projection='3d')
        plt3d.plot_surface(xx, yy, z, alpha=0.4)
        plt.show()


class IntersectionLine(Line):

    def __init__(self):
        Line.__init__(self)
        pass


class Box(object):
    """
    Box in 3D space, constructed from 6 points.

    Parameter:
        xmin - minimum x component
        xmax - maximum x component
        ymin - minimum y component
        ymax - maximum y component
        zmin - minimum z component
        zmax - maximum z component
    """

    def __init__(self, xmin=0, xmax=10, ymin=0, ymax=10, zmin=0, zmax=10):
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        self.ymin = float(ymin)
        self.ymax = float(ymax)
        self.zmin = float(zmin)
        self.zmax = float(zmax)

        self.volume = abs(xmax - xmin) * abs(ymax - ymin) * abs(zmax - zmin)

        self.vmin = np.array([self.xmin, self.ymin, self.zmin])
        self.vmax = np.array([self.xmax, self.ymax, self.zmax])

        self.corners = np.array([[self.xmin, self.ymin, self.zmin],
            [self.xmin, self.ymin, self.zmax],
            [self.xmin, self.ymax, self.zmin],
            [self.xmin, self.ymax, self.zmax],
            [self.xmax, self.ymin, self.zmin],
            [self.xmax, self.ymin, self.zmax],
            [self.xmax, self.ymax, self.zmin],
            [self.xmax, self.ymax, self.zmax]])

    def draw(self):
        """
        Draws given Box in 3D using Matplotlib.
        """

        fig = plt.figure()
        ax = fig.gca(projection='3d')
        # ax = m3d.axes3d(plt.figure())
        plane = [self.corners[i] for i in range(4)]
        rect = m3d.art3d.Poly3DCollection([plane])
        ax.add_collection(rect)

        # Get labels
        ax.set_xlabel('X')
        ax.set_xlim(min(plane[0]) - 5, max(plane[0]) + 5)
        ax.set_ylabel('Y')
        ax.set_ylim(min(plane[1]) - 5, max(plane[1]) + 5)
        ax.set_zlabel('Z')
        ax.set_zlim(min(plane[2]) - 5, max(plane[2]) + 5)

        plt.show()


# Testing things
if __name__ == "__main__":
    print "Specifying a point at 5, 5.5, 6.3"
    p = Point(5, 5.5, 6.3)
    q = Point(5, 2.3, 3.2)
    print p.coordinates[2]

    # l = Line(p.coordinates, q.coordinates)
    # l.draw()
    b = Box(-2, 2, -1.0, 4, 1, 3)
    b.draw()
