from setuptools import setup
from pathlib import Path


# CHANGEME VARS
PACKAGE_NAME = 'nrv-py'
DESCRIPTION = 'NeuRon Virtualizer (NRV)'
AUTHOR_NAME = 'Florian Kolbl, Roland Giraud, Louis Regnacq, Thomas Couppey'
PROJECT_URL = "https://github.com/fkolbl/NRV"
this_directory = Path(__file__).parent
long_description = (this_directory / "ReadMe.md").read_text()

'''
# prevent from unnistalled requierements for nrv import
deps = (
    "gmsh",
    "mph",
    "neuron",
    "icecream",
    "numba",
    "mpi4py",
    "scipy",
    "numpy",
    "ezdxf",
    "dolfinx",
    "petsc4py",
    "ufl",
    "gmsh",
    "dolfinx.io",
    "petsc4py.PETSc",
    "dolfinx.fem",
    "dolfinx.fem.petsc",
    "dolfinx.io.utils",
    "scipy.interpolate",
    "scipy.special",
    "dolfinx.io.gmshio",
    "dolfinx.geometry",
    "dolfinx.mesh",
    "numpy.linalg",
    "matplotlib",
    "matplotlib.pyplot",
    "numpy.core",
    "numpy.core._multiarray_umath",
    "matplotlib._path",
    "scipy.stats",
    "scipy.optimize",
    "matplotlib.pylab",
    "pylab",
    "scipy.spatial",
    "scipy.sparse",
    "scipy.sparse.csgraph",
)
for package in deps:
    sys.modules[package] = MagicMock()
'''

setup(
    # meta infos
    name=PACKAGE_NAME,
    author=AUTHOR_NAME,
    description=DESCRIPTION,
    url=PROJECT_URL,
    version="0.9.15",
    long_description=long_description,
    long_description_content_type='text/markdown',

    # architecture
    packages=[
        "nrv",
        "nrv._misc",
        "nrv._misc.OTF_PP",
        "nrv._misc.comsol_templates",
        "nrv._misc.geom",
        "nrv._misc.log",
        "nrv._misc.materials",
        "nrv._misc.mods",
        "nrv._misc.pops",
        "nrv._misc.ppops",
        "nrv._misc.stats",
        "nrv.backend",
        "nrv.fmod",
        "nrv.fmod.FEM",
        "nrv.fmod.FEM.fenics_utils",
        "nrv.fmod.FEM.mesh_creator",
        "nrv.nmod",
        "nrv.optim",
        "nrv.utils",
        "nrv.utils.cell",
        "nrv.utils.fascicle",
    ],
    
    # non python data to keep
    package_data={
        "nrv": ["nrv2calm"],
        "nrv._misc": ["NRV.ini"],
        "nrv._misc.comsol_templates": ["*.mph"],
        "nrv._misc.geom": ["*.dxf", "*.png"],
        "nrv._misc.log": ["NRV.log"],
        "nrv._misc.materials": ["*.mat"],
        "nrv._misc.mods": ["*.mod"],
        "nrv._misc.pops": ["*.pop"],
        "nrv._misc.ppops": ["*.ppop"],
        "nrv._misc.stats": ["*.csv"],
    },
    include_package_data=True,
    # classifiers
    classifiers=[
        'License :: OSI Approved :: CEA CNRS Inria Logiciel Libre License, version 2.1 (CeCILL-2.1)',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Natural Language :: English',
    ],
    # dependencies
    install_requires=[
        "gmsh",
        "mph",
        "numpy",
        "scipy",
        "neuron",
        "matplotlib",
        "numba",
        "ezdxf",
        "icecream",
    ],  # external packages as dependencies
    python_requires=">=3.9",
)
