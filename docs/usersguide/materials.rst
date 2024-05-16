=========
Materials
=========

Materials properties correspond to a specific class called `material`. This objects hosts the physical constants required to perform the field computations (either anatically or with Finite Elements technique).
For the moment, two properties are inherent to a material:

- the electrical conductivity :math:`{\sigma}` for a material in S.m. This can be a scalar value or an anisotropic property described by atensor corresponding to:

.. math::
    \boldsymbol{\sigma} = \begin{bmatrix}
    \sigma_{xx} & 0 & 0 \\
    0 & \sigma_{yy} & 0 \\
    0 & 0 & \sigma_{zz} \\
    \end{bmatrix}

- the relative dielectric permittivity, used for computation in complex (unitless).

the 'material class can be instanciated by hand, however we recommend for the en user to use files. The usual format is a '.mat' file containing the figures. NRV comes with a list of predefined materials, and it is particularely easy to add new materials, which are both explained bellow.

To load material, the function `load_material` should be always used to ensure reliable code. This function adapts to each following case.

List of pre-defined materials
=============================
Some materials are predefined as routinely used materials and properties. In this case, the argument of the `load_material` function is the string 'name' of the follwing table:

.. list-table:: Tests functionalities
    :widths: 10 10 150
    :header-rows: 1
    :align: center

    *   - Material
        - Name
        - scientific source and comment
    *   - Material
        - 'axoplasmic_mrg'
        - scientific source
    *   - Material
        - 'bone'
        - scientific source
    *   - Material
        - 'cerebrospinal_fluid'
        - scientific source
    *   - Material
        - 'dura'
        - scientific source
    *   - Material
        - 'endoneurium_bahdra'
        - scientific source
    *   - Material
        - 'endoneurium_horn'
        - scientific source
    *   - Material
        - 'endoneurium_ranck'
        - scientific source

How to define a specific material using a .mat file?
====================================================
blablablablablablabla
