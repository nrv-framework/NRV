=========
Materials
=========

Material properties in NRV are encapsulated in the :class:`~nrv.fmod.material` class.  
This object stores the physical constants necessary for field computations, whether analytical or using the Finite Element Method (FEM).

Currently, a material is defined by two intrinsic properties:

- **Electrical conductivity** :math:`\sigma`, expressed in S/m.  
  This can be a scalar value for isotropic media or an anisotropic conductivity tensor:

  .. math::
      \boldsymbol{\sigma} = \begin{bmatrix}
      \sigma_{xx} & 0 & 0 \\
      0 & \sigma_{yy} & 0 \\
      0 & 0 & \sigma_{zz}
      \end{bmatrix}

- **Relative dielectric permittivity** (unitless), used for complex-domain computations.

Although it is possible to instantiate the :class:`~nrv.fmod.material` class manually, it is **strongly recommended** for users to load materials from files—typically in the `.mat` format.  
NRV includes a collection of predefined materials, and adding new custom materials is straightforward. Both use cases are described below.

To load a material, always use the function :meth:`~nrv.fmod.load_material`, which ensures safe and consistent initialization. This function can handle all scenarios transparently.

Predefined Materials
====================

NRV includes a number of commonly used materials with predefined properties.  
To load one of these, use the corresponding name string as an argument to :meth:`~nrv.fmod.load_material`.

.. list-table:: Predefined materials in NRV
    :widths: 20 20 80
    :header-rows: 1
    :align: center

    * - Material
      - Name
      - Scientific source / Notes
    * - Axoplasm
      - ``axoplasmic_mrg``
      - from [m1]
    * - Non-specific bone
      - ``bone``
      - from [m2]
    * - Cerebrospinal fluid
      - ``cerebrospinal_fluid``
      - from [m3]
    * - Dura mater
      - ``dura``
      - from [m3]
    * - Endoneurium (Bhadra)
      - ``endoneurium_bahdra``
      - from [m6], isotropic, not from direct measurement
    * - Endoneurium (Horn)
      - ``endoneurium_horn``
      - from [m5]
    * - Endoneurium (Ranck)
      - ``endoneurium_ranck``
      - from [m4]
    * - Epidural space
      - ``epidural_space``
      - from [m3]
    * - Epineurium (Horn)
      - ``epineurium_horn``
      - from [m5]
    * - Epineurium (generic)
      - ``epineurium``
      - unspecified source
    * - Muscle (average)
      - ``muscle``
      - average of different muscle types, from [m3]
    * - Perineurium (Horn)
      - ``perineurium_horn``
      - from [m5]
    * - Perineurium (generic)
      - ``perineurium``
      - unspecified source
    * - Platinum
      - ``platinum``
      - commonly cited values
    * - Saline solution
      - ``saline``
      - commonly cited values
    * - Silicone
      - ``silicone``
      - commonly cited values

All predefined materials are located in the following directory of the NRV package:  
``nrv/_misc/materials/``

Scientific References
=====================

References for the materials listed above:

- [m1] McIntyre, C. C., Richardson, A. G., & Grill, W. M. (2002). *Modeling the excitability of mammalian nerve fibers: influence of afterpotentials on the recovery cycle*. Journal of Neurophysiology, 87(2), 995–1006.

- [m2] Kosterich, J. D., Foster, K. R., & Pollack, S. R. (1983). *Dielectric permittivity and electrical conductivity of fluid saturated bone*. IEEE Transactions on Biomedical Engineering, (2), 81–86.

- [m3] Gabriel, C., & Gabriel, S. (1996). *Compilation of the dielectric properties of body tissues at RF and microwave frequencies*.

- [m4] Ranck Jr, J. B., & BeMent, S. L. (1965). *The specific impedance of the dorsal columns of cat: an anisotropic medium*. Experimental Neurology, 11(4), 451–463.

- [m5] Horn, M. R., Vetter, C., Bashirullah, R., Carr, M., & Yoshida, K. (2023). *Characterization of the electrical properties of mammalian peripheral nerve laminae*. Artificial Organs, 47(4), 705–720.

- [m6] Bhadra, N., Lahowetz, E. A., Foldes, S. T., & Kilgore, K. L. (2007). *Simulation of high-frequency sinusoidal electrical block of mammalian myelinated axons*. Journal of Computational Neuroscience, 22, 313–326.


How to Define a Custom Material Using a `.mat` File
====================================================

It is possible to define and add custom materials to NRV by creating a `.mat` file.  
This file can either be:

- Placed directly into the `nrv/_misc/materials/` folder (in which case it becomes accessible via its name), or  
- Stored locally and loaded via its full path when calling the :meth:`~nrv.fmod.load_material` function.

When stored in the default folder, the material can be loaded simply by passing the file name **without** the `.mat` extension to `load_material`.

Structure of a Custom `.mat` File
---------------------------------

A `.mat` material file must contain a dictionary of values with the following keys:

.. list-table:: Expected content of a `.mat` material file
    :widths: 30 70
    :header-rows: 1
    :align: center

    * - Key
      - Description
    * - ``name``
      - Name of the material. Important when the material defines part of a nerve (e.g., `perineurium`, `epineurium`, `endoneurium`).
    * - ``source``
      - Optional string for documentation or comments. Not used internally by NRV.
    * - ``sigma``
      - Electrical conductivity (in S/m) for isotropic materials.
    * - ``sigma_xx``
      - Electrical conductivity along the x-axis (longitudinal). Required for **anisotropic** materials.
    * - ``sigma_yy``
      - Electrical conductivity along the y-axis (radial). Required for **anisotropic** materials.
    * - ``sigma_zz``
      - Electrical conductivity along the z-axis (radial). Required for **anisotropic** materials.
    * - ``epsilon_r``
      - Relative dielectric permittivity (unitless).

.. note::
   For anisotropic materials, you **must** define all three tensor components (`sigma_xx`, `sigma_yy`, `sigma_zz`).  
   For isotropic materials, use only `sigma`.

This approach provides a flexible way to extend NRV with application-specific materials or experimentally measured data.
