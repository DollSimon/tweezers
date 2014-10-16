from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from itertools import product, combinations

# fig = plt.figure()
# ax = fig.gca(projection='3d')
# ax.set_aspect("equal")
#
# #draw cube
# r = [-1, 1]
# for s, e in combinations(np.array(list(product(r, r, r))), 2):
#     if np.sum(np.abs(s - e)) == r[1] - r[0]:
#         ax.plot3D(*zip(s, e), color="b")
#
# plt.show()
