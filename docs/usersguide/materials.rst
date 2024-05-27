=========
Materials
=========

Materials properties correspond to a specific class called `material`. This object hosts the physical constants required to perform the field computations (either anatically or with Finite Elements technique).
For the moment, two properties are inherent to a material:

- The electrical conductivity :math:`{\sigma}` for a material in S.m. This can be a scalar value or an anisotropic property described by atensor corresponding to:

.. math::
    \boldsymbol{\sigma} = \begin{bmatrix}
    \sigma_{xx} & 0 & 0 \\
    0 & \sigma_{yy} & 0 \\
    0 & 0 & \sigma_{zz} \\
    \end{bmatrix}

- The relative dielectric permittivity, used for computation in complex (unitless).

The `material` class can be instantiated by hand, however we recommend for the en user to use files. The usual format is a '.mat' file containing the figures. NRV comes with a list of predefined materials, and it is particularely easy to add new materials, which are both explained bellow.

To load material, the function `load_material` should be always used to ensure reliable code. This function adapts to each following case.

List of pre-defined materials
=============================
Some materials are predefined as routinely used materials and properties. In this case, the argument of the `load_material` function is the string 'name' of the follwing table:

.. list-table:: pre-defined materials in NRV
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Material
        - Name
        - scientific source and comment
    *   - Axoplasm
        - "axoplasmic_mrg"
        - from reference [m1]
    *   - non-specific bone
        - "bone"
        - from reference [m2]
    *   - Cerebrospinal fluid
        - "cerebrospinal_fluid"
        - from reference [m3]
    *   - Dura mater
        - "dura"
        - from reference [m3]
    *   - Endoneurium
        - "endoneurium_bahdra"
        - figure from reference [m6], isotropic material, corresponds to no meausrement
    *   - Endoneurium
        - "endoneurium_horn"
        - figures from reference [m5]
    *   - Endoneurium
        - "endoneurium_ranck"
        - figures from reference [m4]
    *   - Averaged epidurial space
        - "epidural_space"
        - from reference [m3]
    *   - Epineurium
        - "epineurium_horn"
        - figures from reference [m5]
    *   - Epineurium
        - "epineurium"
        - scientific source
    *   - Average muscle
        - "muscle"
        - do not corresponds specifically to smooth, skeletal or cardiac muscle, from reference [m3]
    *   - Perineurium
        - "perineurium_horn"
        - figures from reference [m5]
    *   - Perineurium
        - "perineurium"
        - scientific source
    *   - Platinum
        - "platinum"
        - commonly found value
    *   - Saline solution
        - "saline"
        - commonly found value
    *   - Silicone
        - "silicone"
        - commonly found value

All the pre-defined material are located in a folder inside the NRV package with the path `nrv/_misc/materials/`.

Here is the list of exact scientific references used to write pre-defined materials:

- [m1] McIntyre, C. C., Richardson, A. G., & Grill, W. M. (2002). Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle. Journal of neurophysiology, 87(2), 995-1006.

- [m2] Kosterich, J. D., Foster, K. R., & Pollack, S. R. (1983). Dielectric permittivity and electrical conductivity of fluid saturated bone. IEEE Transactions on biomedical engineering, (2), 81-86.

- [m3] Gabriel, C., & Gabriel, S. (1996). Compilation of the dielectric properties of body tissues at RF and microwave frequencies.

- [m4] Ranck Jr, J. B., & BeMent, S. L. (1965). The specific impedance of the dorsal columns of cat: an anisotropic medium. Experimental neurology, 11(4), 451-463.

- [m5] Horn, M. R., Vetter, C., Bashirullah, R., Carr, M., & Yoshida, K. (2023). Characterization of the electrical properties of mammalian peripheral nerve laminae. Artificial organs, 47(4), 705-720.

- [m6] Bhadra, N., Lahowetz, E. A., Foldes, S. T., & Kilgore, K. L. (2007). Simulation of high-frequency sinusoidal electrical block of mammalian myelinated axons. Journal of computational neuroscience, 22, 313-326.



How to define a specific material using a .mat file?
====================================================
It is possible to add new materials by defining a `.mat`` file. This file can be directly added in the `nrv/_misc/materials/`. In this case, to load the material, just the filename without the `.mat` extension is the corresponding loading string. It is also possible to define locally a `.mat` file and give the path as argument to the `load_material` function.

In this case, the `.mat` file is a simple of list of values arranged with the following keys:

.. list-table:: Content of the `.mat file`
    :widths: 50 150
    :header-rows: 1
    :align: center

    *   - name
        - name of the material, important if constitutive of the nerve (perineurium, epineurium, endoneurium)
    *   - source
        - free comment for user purpose, not interpreted by NRV
    *   - sigma
        - electrical conductivity, **if the material is isotropic**
    *   - sigma_xx
        - electrical conductivity along the x-axis (longitudinal), **if the material is anisotropic**
    *   - sigma_yy
        - electrical conductivity along the y-axis (radial), **if the material is anisotropic**
    *   - sigma_zz
        - electrical conductivity along the y-axis (radial), **if the material is anisotropic**
    *   - epsilon_r
        - relative permittivity of the material