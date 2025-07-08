r"""
Axon Population Placement in Various Shapes
===========================================

This example demonstrates how to:
    - Create axon populations for different shapes (circle, ellipse, polygon)
    - Place axons using both direct data and the placer
    - Use and highlight various placer arguments (delta, delta_trace, delta_in, method, fit_to_size, n_iter)

.. seealso::
    :doc:`Users' guide <../../usersguide/populations>`
"""

import matplotlib.pyplot as plt
import numpy as np
from nrv.utils import geom
from nrv.nmod._axon_population import axon_population

# %%
# Placement in a Circle using the placer
# --------------------------------------
center = (0, 0)
radius = 100
n_ax = 625

pop_circle = axon_population()
pop_circle.set_geometry(center=center, radius=radius)
pop_circle.create_population_from_stat(n_ax=n_ax)
pop_circle.place_population(delta=2)  # default placer
pop_circle.get_ppop_info(verbose=True)

# %%
# Placement in an Ellipse using the placer with custom delta
# ----------------------------------------------------------
center_ellipse = (200, 0)
r_ellipse = (120, 60)
angle = np.pi/6

pop_ellipse = axon_population()
pop_ellipse.set_geometry(center=center_ellipse, radius=r_ellipse, rot=angle)
pop_ellipse.create_population_from_stat(n_ax=n_ax)
pop_ellipse.place_population(delta=2)
pop_ellipse.get_ppop_info(verbose=True)

# %%
# Placement in a Polygon using the placer and `delta`
# ---------------------------------------------------

vertices = [(-100, 100), (0, 200), (100, 100), (60, 0), (0, -100), (-60, 0)]
pop_polygon = axon_population()
poly = geom.Polygon(vertices=vertices)
pop_polygon.set_geometry(geometry=poly)
pop_polygon.create_population_from_stat(n_ax=n_ax)
pop_polygon.place_population(delta_in=2, delta_trace=20)
pop_polygon.get_ppop_info(verbose=True)

# %%
# Placement from data (direct y/z)
# --------------------------------
#
# Generate mesh grid position inside the circle bounding box

x = np.linspace(-radius, radius, int(n_ax**0.5))
xv, yv = np.meshgrid(x, x)
xv = xv.reshape((n_ax,))
yv = yv.reshape((n_ax,))
types = np.random.randint(0, 2, n_ax)
n_mye = types.sum()
diameters = np.zeros(n_ax)
diameters[types.astype(bool)] = np.random.uniform(2, 11, n_mye)
diameters[~types.astype(bool)] = np.random.uniform(.1,4, n_ax-n_mye)

pop_data = axon_population()
pop_data.set_geometry(center=center, radius=radius)
pop_data.create_population_from_data((types, diameters, xv, yv))
pop_data.get_ppop_info(verbose=True)

# %%
# Placement using the "packing" method
# ------------------------------------

pop_packing = axon_population()
pop_packing.set_geometry(center=center, radius=radius)
pop_packing.create_population_from_stat(n_ax=n_ax)
pop_packing.place_population(method="packing", delta=2, fit_to_size=True, n_iter=16000)
pop_packing.get_ppop_info(verbose=True)


# %%
# All in one using :meth:`~nrv.nmod.axon_population.generate`
# -----------------------------------------------------------

pop_fvf = axon_population()
pop_fvf.generate(center=center, radius=radius, n_ax=n_ax, delta_in=3)
pop_fvf.get_ppop_info(verbose=True)

# %%
# Plotting

def plot_pop(axes:plt.Axes, pop:axon_population, title:str):
    """
    Plot an axon population in `axes`
    """
    pop.plot(axes)
    axes.set_title(title)
    axes.set_aspect('equal', adjustable='box')
    axes.set_xlabel('Y-axis')
    axes.set_ylabel('Z-axis')

fig, axs = plt.subplots(2, 3, figsize=(15, 10))
plot_pop(axs[0, 0], pop_circle, "Circle - placer (delta=2)")
plot_pop(axs[0, 1], pop_ellipse, "Ellipse - placer (delta=2, n_iter=2000)")
plot_pop(axs[0, 2], pop_polygon, "Polygon - placer (delta_in=2, delta_trace=10)")
plot_pop(axs[1, 0], pop_data, "Circle - from data (direct y/z)")
plot_pop(axs[1, 1], pop_packing, "Circle - packing (fit_to_size=True, n_iter=17000)")
plot_pop(axs[1, 2], pop_fvf, "Circle - generate")

plt.show()
