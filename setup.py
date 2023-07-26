from setuptools import setup
from unittest.mock import MagicMock    # mock imports
import sys

# prevent from unnistalled requierements for nrv
deps = ('mph', 'neuron', 'icecream', 'numba', 'mpi4py', 'scipy', 
        'numpy', 'ezdxf', 'dolfinx', 'petsc4py', 'ufl', 'gmsh', 'dolfinx.io', 
        'petsc4py.PETSc', 'dolfinx.fem', 'dolfinx.fem.petsc', 'dolfinx.io.utils',
        'scipy.interpolate', 'scipy.special', 'dolfinx.io.gmshio', 'dolfinx.geometry',
        'dolfinx.mesh', 'numpy.linalg',  'matplotlib', 'matplotlib.pyplot', 'numpy.core', 
        'numpy.core._multiarray_umath', 'matplotlib._path', 'scipy.stats', 'scipy.optimize',
        'matplotlib.pylab', 'pylab', 'scipy.spatial', 'scipy.sparse', 'scipy.sparse.csgraph')
for package in deps:
    sys.modules[package] = MagicMock()

import nrv

setup(
   name='nrv-py',
   version=nrv.__version__,
   description=nrv.__project__,
   long_description = 'file: README.md',
   author=nrv.__contributors__,
   packages=['nrv'],
   include_package_data = True,
   url = 'https://github.com/fkolbl/NRV',
   classifiers =[
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent'
     ],
    install_requires=['mph', 'numpy','scipy','neuron','matplotlib','numba','ezdxf','icecream'], #external packages as dependencies
    python_requires = '>=3.6'
)
