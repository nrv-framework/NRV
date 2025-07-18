
.. DO NOT EDIT.
.. THIS FILE WAS AUTOMATICALLY GENERATED BY SPHINX-GALLERY.
.. TO MAKE CHANGES, EDIT THE SOURCE PYTHON FILE:
.. "examples/generic/25_test_fit_fasc.py"
.. LINE NUMBERS ARE GIVEN BELOW.

.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        :ref:`Go to the end <sphx_glr_download_examples_generic_25_test_fit_fasc.py>`
        to download the full example code.

.. rst-class:: sphx-glr-example-title

.. _sphx_glr_examples_generic_25_test_fit_fasc.py:


Simulation of Realistic Geometry
================================

Practical example illustrating how to build a realistic nerve geometry from an image and simulate it with NRV.

.. warning::
    This example requires `opencv-python <https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html>`_ to be installed. You can easily install this library with pip:
    
    .. code-block:: bash

        pip install opencv-python

.. GENERATED FROM PYTHON SOURCE LINES 15-27

.. code-block:: Python

    import nrv

    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.interpolate import splprep, splev

    image_path = nrv.__path__[0] + "/_misc/geom/smoothed_edges_white.png"

    d_nerve = 1_000 # um
    l_nerve = 10_000 # um








.. GENERATED FROM PYTHON SOURCE LINES 28-36

Step 1: Load and process the image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
      Since the image is already processed, the following function is quite light. Additional processing would be required to generate a nerve directly from histology images.

.. tip::
      See `opencv-python <https://docs.opencv.org/4.x/d3/d05/tutorial_py_table_of_contents_contours.html>`_ contour tutorials for more information.

.. GENERATED FROM PYTHON SOURCE LINES 36-48

.. code-block:: Python


    def load_and_process_image(ax:plt.Axes)->np.ndarray:
        """
        Load the image and process it to simplify contour detection.
        """
        im = cv2.imread(image_path)    # Load image
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        ax.imshow(im, label="image")
        ax.set_title("Original image ($nrv/\\_misc/geom/$)")
        return thresh








.. GENERATED FROM PYTHON SOURCE LINES 49-54

Step 2: Extract contour points from the image
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. note::
       This function is adapted to the selected image and can be improved for nerve histological images.

.. GENERATED FROM PYTHON SOURCE LINES 54-97

.. code-block:: Python


    def extract_contour_points(ax:plt.Axes, thresh)->list:
        """
        Detect all contours in the image and keep only the points from fascicle contours. Additionally, rescale the point positions from pixels to micrometers to match the desired nerve diameter.
        """

        # Detect contours on the binary image using cv2.CHAIN_APPROX_SIMPLE
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        hc_list = hierarchy.squeeze()

        # ID of the inner nerve contour
        # As image frame is 0, outer_nerve is 1
        nerve_id = 2 

        # Center nerve at (0,0)
        points = contours[nerve_id].squeeze()
        center_pix = np.mean(points, axis=0)
        nerve_points = points - center_pix

        # Convert pixel index to micrometers
        radius_pix = np.max(np.abs(nerve_points))
        rescal_factor = d_nerve / (2 * radius_pix)
        # Flip ordinate axis (as pixel index increases downward)
        rescal_factor *= np.array([1, -1])

        nerve_points *= rescal_factor

        ax.plot(*nerve_points.T, "--", color=("k", .3))

        theta = np.linspace(0, 2 * np.pi)
        ax.plot(d_nerve * np.cos(theta) / 2, d_nerve * np.sin(theta) / 2, color="k")

        fascicles_points = []
        for _i, _c in enumerate(contours):
            if hc_list[_i, -1] == nerve_id:
                points = _c.squeeze()
                fascicles_points += [(points - center_pix) * rescal_factor]
                ax.plot(*fascicles_points[-1].T)
        ax.set_aspect("equal")
        ax.set_title("Extracted contours")

        return fascicles_points








.. GENERATED FROM PYTHON SOURCE LINES 98-100

Step 3: Generate a nerve from fascicle contour points
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. GENERATED FROM PYTHON SOURCE LINES 100-144

.. code-block:: Python


    def generate_nerve(ax:plt.Axes, fascicles_points:list):
        """
        Generate a nerve from the fascicle contour points, with a LIFE electrode at the center of the first fascicle.
        """
        ner = nrv.nerve(diameter=d_nerve, length=l_nerve)
        n_vertices = 50
        for _i_fasc, _pts in enumerate(fascicles_points):
            i_pts = np.arange(n_vertices + 1) * _pts.shape[0] // n_vertices
            i_pts[-1] -= 1
            _us_pts = _pts[i_pts]  # Undersample the vertices
            poly_fasc = nrv.create_cshape(vertices=_us_pts)
            fasc = nrv.fascicle(ID=_i_fasc)
            fasc.set_geometry(geometry=poly_fasc)
            ner.add_fascicle(fasc)

        for fasc in ner.fascicles.values():
            fasc.fill(n_ax=100, delta_trace=10)

        extra_stim = nrv.FEM_stimulation(endo_mat="endoneurium_ranck", peri_mat="perineurium", epi_mat="epineurium", ext_mat="saline")

        life_d = 25                                 # LIFE diameter in um
        life_length = 1000                          # LIFE active-site length in um
        life_x_offset = (l_nerve - life_length) / 2 # x position of the LIFE (centered)
        life_y_c_2, life_z_c_2 = ner.fascicles[0].center  # LIFE_2 y-coordinate (in um)

        elec_2 = nrv.LIFE_electrode("LIFE_2", life_d, life_length, life_x_offset, life_y_c_2, life_z_c_2) # LIFE in fascicle 2

        # Stimulus
        t_start = 0.1       # Start of the pulse, in ms
        t_pulse = 0.1       # Duration of the pulse, in ms
        amp_pulse = 60      # Amplitude of the pulse, in uA 

        pulse_stim = nrv.stimulus()
        pulse_stim.pulse(t_start, -amp_pulse, t_pulse)      # Cathodic

        # Attach electrodes to the extra_stim object 
        extra_stim.add_electrode(elec_2, pulse_stim)
        ner.attach_extracellular_stimulation(extra_stim)

        ner.plot(ax)
        ax.set_title("NRV geometry")
        return ner








.. GENERATED FROM PYTHON SOURCE LINES 145-147

Step 4: Simulate the nerve and plot recruited fibers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. GENERATED FROM PYTHON SOURCE LINES 147-154

.. code-block:: Python

    def simulate_and_plot_res(ax:plt.Axes, ner:nrv.nerve):
        res = ner.simulate(t_sim=3, postproc_script="is_recruited")
        res.plot_recruited_fibers(ax)
        ax.set_title("Recruited Fibers")
        ax.set_xlabel("z-axis (µm)")
        ax.set_ylabel("y-axis (µm)")








.. GENERATED FROM PYTHON SOURCE LINES 155-157

Main Execution Script
^^^^^^^^^^^^^^^^^^^^^

.. GENERATED FROM PYTHON SOURCE LINES 157-166

.. code-block:: Python

    if __name__ == "__main__":
        plt.ion()
        fig, axs = plt.subplots(2, 2, figsize=(10, 6), layout="constrained")

        thresh = load_and_process_image(axs[0, 0])
        fasc_pts = extract_contour_points(axs[0, 1], thresh)
        ner = generate_nerve(axs[1, 0], fasc_pts)
        simulate_and_plot_res(axs[1, 1], ner)
        plt.show()



.. image-sg:: /examples/generic/images/sphx_glr_25_test_fit_fasc_001.png
   :alt: Original image ($nrv/\_misc/geom/$), Extracted contours, NRV geometry, Recruited Fibers
   :srcset: /examples/generic/images/sphx_glr_25_test_fit_fasc_001.png
   :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 .. code-block:: none

    NRV INFO: On 100 axons to generate, there are 30 Myelinated and 70 Unmyelinated
    Placing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    NRV INFO: On 100 axons to generate, there are 30 Myelinated and 70 Unmyelinated
    Placing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    NRV INFO: On 100 axons to generate, there are 30 Myelinated and 70 Unmyelinated
    Placing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    NRV INFO: On 100 axons to generate, there are 30 Myelinated and 70 Unmyelinated
    Placing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00
    NRV INFO: Starting nerve simulation
    NRV INFO: ...computing electrodes footprint
    NRV INFO: Mesh properties:
    NRV INFO: Number of processes : 3
    NRV INFO: Number of entities : 2348
    NRV INFO: Number of nodes : 10758
    NRV INFO: Number of elements : 64466
    NRV INFO: Static/Quasi-Static electrical current problem
    NRV INFO: FEN4NRV: setup the bilinear form
    NRV INFO: FEN4NRV: setup the linear form
    NRV INFO: Static/Quasi-Static electrical current problem
    NRV INFO: FEN4NRV: solving electrical potential
    NRV INFO: FEN4NRV: solved in 16.50598931312561 s
    fascicle 1/4 -- 3 CPUs: 100 / 100 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:20
    fascicle 2/4 -- 3 CPUs: 100 / 100 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:18
    fascicle 3/4 -- 3 CPUs: 100 / 100 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:17
    fascicle 4/4 -- 3 CPUs: 100 / 100 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00 0:00:19
    NRV INFO: ...Done!





.. rst-class:: sphx-glr-timing

   **Total running time of the script:** (1 minutes 44.168 seconds)


.. _sphx_glr_download_examples_generic_25_test_fit_fasc.py:

.. only:: html

  .. container:: sphx-glr-footer sphx-glr-footer-example

    .. container:: sphx-glr-download sphx-glr-download-jupyter

      :download:`Download Jupyter notebook: 25_test_fit_fasc.ipynb <25_test_fit_fasc.ipynb>`

    .. container:: sphx-glr-download sphx-glr-download-python

      :download:`Download Python source code: 25_test_fit_fasc.py <25_test_fit_fasc.py>`

    .. container:: sphx-glr-download sphx-glr-download-zip

      :download:`Download zipped: 25_test_fit_fasc.zip <25_test_fit_fasc.zip>`
