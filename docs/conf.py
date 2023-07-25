# Configuration file for the Sphinx documentation builder.
import os
import sys

sys.path.insert(0, os.path.abspath('..'))


# -- Project information -----------------------------------------------------
import nrv

project = nrv.__project__
copyright = nrv.__copyright__
author = nrv.__contributors__
release = nrv.__version__


# -- General configuration ---------------------------------------------------

extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc', 'sphinx.ext.napoleon','sphinx_rtd_theme']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------


# Rendering options
myst_heading_anchors = 2               # Generate link anchors for sections.
html_copy_source     = False           # Copy documentation source files?
html_show_copyright  = False           # Show copyright notice in footer?
html_show_sphinx     = False           # Show Sphinx blurb in footer?

# Rendering style
html_theme          = 'furo'           # custom theme with light and dark mode
pygments_style      = 'friendly'       # syntax highlight style in light mode
pygments_dark_style = 'stata-dark'     # syntax highlight style in dark mode
html_static_path    = ['style']        # folders to include in output
html_css_files      = ['custom.css']   # extra style files to apply
