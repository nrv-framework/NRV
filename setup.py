from setuptools import setup

# CHANGEME VARS
PACKAGE_NAME = 'nrv-py'
DESCRIPTION = 'NeuRon Virtualizer (NRV)'
AUTHOR_NAME = 'Florian Kolbl, Roland Giraud, Louis Regnacq, Thomas Couppey'
PROJECT_URL = "https://github.com/fkolbl/NRV"

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
    version='{{VERSION_PLACEHOLDER}}',
    author=AUTHOR_NAME,
    description=DESCRIPTION,
    url=PROJECT_URL,

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
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    # dependencies
    install_requires=[
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
