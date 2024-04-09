# Configuration file for the Sphinx documentation builder.
import os
import sys
from unittest.mock import MagicMock  # mock imports

sys.path.insert(0, os.path.abspath(".."))

html_css_files = [
    'custom.css',
]

# prevent from unnistalled requierements for nrv
deps = (
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
    "dolfinx.cpp",
    "dolfinx.cpp.mesh",
    "numpy.linalg",
    "matplotlib",
    "matplotlib.pyplot",
    "matplotlib.pylab",
    "matplotlib.animation",
    "numpy.core",
    "numpy.core._multiarray_umath",
    "matplotlib._path",
    "scipy.stats",
    "scipy.optimize",
    "scipy.constants",
    "pylab",
    "scipy.spatial",
    "scipy.sparse",
    "scipy.sparse.csgraph",
    "scipy.signal",
    "pyswarms",
    "pyswarms.utils",
    "pyswarms.backend.topology",
)
for package in deps:
    sys.modules[package] = MagicMock()

import nrv

# -- Project information -----------------------------------------------------
project = nrv.__project__
copyright = nrv.__copyright__
author = nrv.__contributors__
release = nrv.__version__
version = release

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------
# Web site
html_title = f"{project} {version}"  # document title
html_logo = "images/logo.png"  # project logo

# Rendering options
myst_heading_anchors = 2  # Generate link anchors for sections.
html_copy_source = False  # Copy documentation source files?
html_show_copyright = False  # Show copyright notice in footer?
html_show_sphinx = False  # Show Sphinx blurb in footer?

# Rendering style
html_theme = "furo"  # custom theme with light and dark mode
pygments_style = "friendly"  # syntax highlight style in light mode
pygments_dark_style = "stata-dark"  # syntax highlight style in dark mode
html_static_path = ["style"]  # folders to include in output
html_css_files = ["custom.css"]  # extra style files to apply

# Sources options
autodoc_member_order = 'bysource' # keep the order of class and function source files
#                                   (thus don't use alphabetical order)