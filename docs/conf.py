# Configuration file for the Sphinx documentation builder.
import os
import sys
from unittest.mock import MagicMock
from pygments.styles import get_all_styles
# from sphinx_gallery.sorting import FileNameSortKey
# Insert project root to path
sys.path.insert(0, os.path.abspath(".."))

# List of styles for syntax highlighting
styles = list(get_all_styles())
    # ... your mocking code ...
    # Prevent from unnistalled requirements for nrv
    # Please add them in alphabetical order to avoid repetition.
deps = (
    "basix",
    "basix.ufl",
    "dolfinx",
    "dolfinx.cpp",
    "dolfinx.cpp.mesh",
    "dolfinx.fem",
    "dolfinx.fem.petsc",
    "dolfinx.geometry",
    "dolfinx.mesh",
    "dolfinx.io",
    "dolfinx.io.gmshio",
    "dolfinx.io.utils",
    "scipy.special",
    "ezdxf",
    "gmsh",
    "icecream",
    "mph",
    "mpi4py",
    "mpi4py.MPI",
    "neuron",
    "numba",
    "pandas",
    "pathos",
    "pathos.multiprocessing",
    "petsc4py",
    "petsc4py.PETSc",
    "psutil",
    "pylab",
    "pyswarms",
    "pyswarms.backend.topology",
    "pyswarms.utils",
    "rich",
    "rich.progress",
    "scipy",
    "scipy.constants",
    "scipy.interpolate",
    "scipy.optimize",
    "scipy.signal",
    "scipy.sparse",
    "scipy.sparse.csgraph",
    "scipy.spatial",
    "scipy.stats",
    "shapely",
    "ufl",
    "ufl.finiteelement",
    "pathos",
    "pathos.multiprocessing",
)

try:
    import nrv
    deps_installed = True
except:
    deps_installed = False
    # Packages that must not be mocked (used at runtime by sphinx-gallery and others)
    do_not_mock = {"matplotlib", "numpy"}

    # Apply mocks
    for package in deps:
        if package.split('.')[0] not in do_not_mock:
            sys.modules[package] = MagicMock()

    # Import your project after mocking
    import nrv

# -- Project information -----------------------------------------------------
project = nrv.__project__
copyright = nrv.__copyright__
author = nrv.__contributors__
release = nrv.__version__
version = release

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx_gallery.gen_gallery',
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx.ext.mathjax",
    "sphinx_mdinclude",
    "sphinx_rtd_theme",
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
    "sphinx_codeautolink",
]

# Templates path
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "examples/__nodoc", "__logo/__build"]

# Source file suffixes
source_suffix = [".rst", ".md"]

# -- Options for HTML output -------------------------------------------------
html_title = f"{project} {version}"
html_logo = "__logo/logo.png"

# Rendering options
myst_heading_anchors = 2
html_copy_source = False
html_show_copyright = False
html_show_sphinx = False

# Theme and style
html_theme = "furo"
pygments_style = "friendly"
pygments_dark_style = "stata-dark"
html_static_path = ["style"]
html_css_files = ["custom.css"]
highlight_language = "python3"

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "matplotlib": ("https://matplotlib.org/stable/", None),
}

# Napoleon config
napoleon_include_special_with_doc = True

# Autodoc config
autodoc_member_order = 'bysource'
autosummary_generate = True
autosummary_ignore_module_all = False

# nbsphinx config
nbsphinx_execute = 'never'

# -- Sphinx Gallery configuration ---------------------------------------------
sphinx_gallery_conf = {
   
    'examples_dirs': ['../examples','../tutorials'], # Example scripts path
    'gallery_dirs': ['examples','tutorials'], # Path where to save gallery output
    'filename_pattern': r'.py$',  # exclude files with __nodoc in name
    'ignore_pattern': r'__nodoc',
    'show_signature': False,        # Show source links in generated gallery
    'thumbnail_size': (300, 300),   # Thumbnail size
    'default_thumb_file': "docs/"+html_logo, # Default Thumbnail image
    'within_subsection_order': "FileNameSortKey",  # sort files alphabetically  # needs this: from sphinx_gallery.sorting import FileNameSortKey
    'matplotlib_animations': True, # Matplotlib backend to use
    'download_all_examples': False, # Remove "Download all examples" button (optional)
    'remove_config_comments': True, # Avoid re-executing examples if nothing changed
}

