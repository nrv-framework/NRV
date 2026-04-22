r"""
Intracellular stimulation of axon subpopulations
================================================

Example of use of subpopulation for axon species targeted current clamp.

This example shows:
    - Creating a nerve with fascicles of various geometries.
    - Filling fascicles with axon populations.
    - Selecting subpopulations using expressions or masks.
    - Applying IClamp to specific subpopulations.
    - Running a simulation and plotting recruited fibers.

.. seealso::
    - :doc:`Simulable <../../usersguide/populations>`, :doc:`Axon population <../../usersguide/populations>` and :doc:`Geometry <../../usersguide/geometry>` Users' guides.
    
     - :doc:`Tutorial 4 <../../tutorials/4_nerve_simulation>`
"""

import nrv
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # --- Nerve and Fascicle Setup ---
    ner = nrv.nerve(length=5000, diameter=500, Outer_D=5)

    # Fascicle 1: Circle
    fasc1 = nrv.fascicle(diameter=200, ID=1)
    fasc1_y, fasc1_z = -100, -60
    ner.add_fascicle(fasc1, y=fasc1_y, z=fasc1_z)

    # Fascicle 2: Ellipse
    fasc2 = nrv.fascicle(ID=2)
    fasc2.set_geometry(diameter=(120, 60), rot=30, degree=True)
    fasc2_y, fasc2_z = 100, -70
    ner.add_fascicle(fasc2, y=fasc2_y, z=fasc2_z)

    # Fascicle 3: Polygon
    vertices = [(-80, 130), (0, 180), (80, 130), (50, 30), (0, -30), (-50, 30)]
    fasc3 = nrv.fascicle(ID=3)
    fasc3.set_geometry(geometry=nrv.create_cshape(vertices=vertices))
    fasc3_y, fasc3_z = 0, 100
    ner.add_fascicle(fasc3, y=fasc3_y, z=fasc3_z, rot=-np.pi/6)

    # --- Fill fascicles with axon populations ---
    n_ax = 200
    for fasc in ner.fascicles.values():
        fasc.fill(n_ax=n_ax, percent_unmyel=0.7, delta=2)

    # --- Plot nerve ---
    fig, ax = plt.subplots(figsize=(7, 7))
    ner.plot(ax)

    # --- Select subpopulations and apply IClamp ---
    # Example: stimulate only large-diameter axons in fascicle 1, and only unmyelinated in fascicle 3
    i_pos = 0.5
    i_start = 0.2
    i_dur = 0.5
    i_amp = 2.0

    # For fascicle 1: select axons with diameter > 8 um
    expr_large = "diameters > 8"
    fasc1.insert_I_Clamp(
        position=i_pos,  # middle of axon
        t_start=i_start,
        duration=i_dur,
        amplitude=i_amp,  # nA
        expr=expr_large
    )

    # For fascicle 2: select unmyelinated axons
    expr_local = f"(y-{fasc2_y})**2 + (z-{fasc2_z})**2 < 25**2"
    mask_local = fasc2.axons.get_mask(expr=expr_local, otype="list")
    fasc2.insert_I_Clamp(
        position=i_pos,
        t_start=i_start,
        duration=i_dur,
        amplitude=i_amp,
        ax_list=mask_local,
    )

    # For fascicle 3: stimulate only large unmyelinated axons
    expr_unmyel = "types == 0"
    fasc2.axons.add_mask(data=expr_unmyel, label="umyel")
    expr_ularge = "diameters > 1"
    mask_u = fasc2.axons.add_mask(data=expr_ularge, label="ularge")
    
    fasc3.insert_I_Clamp(
        position=i_pos,
        t_start=i_start,
        duration=i_dur,
        amplitude=i_amp,
        mask_labels=["umyel", "ularge"],
    )

    # --- Run simulation ---
    results = ner.simulate(t_sim=2, postproc_script="is_recruited")


# %%
# Plot recruited fibers
# ^^^^^^^^^^^^^^^^^^^^^
if __name__ == '__main__':
    fig, ax = plt.subplots(figsize=(7, 7))
    results.plot_recruited_fibers(ax)
    ax.set_xlabel("z-axis (µm)")
    ax.set_ylabel("y-axis (µm)")
    ax.set_title("Recruited fibers after IClamp on subpopulations")
    plt.show()

# sphinx_gallery_thumbnail_number = -1
