# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
import os

# -- Path setup --------------------------------------------------------------

# Custom extensions
sys.path.insert(0, os.path.abspath("../_ext"))

# CACE
sys.path.insert(0, os.path.abspath('../..'))
from cace import __version__

# -- Project information -----------------------------------------------------

project = 'CACE'
copyright = '2026, CACE Contributors'
author = 'Tim Edwards, Leo Moser'
release = __version__

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

custom_extensions = [
    'generate_docs',
]
third_party_extensions = [
    'myst_parser'
]
extensions = third_party_extensions + custom_extensions

source_suffix = {
    '.md': 'markdown',
    '.rst': 'restructuredtext',
}

root_doc = "index"

templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "venv",
    "install",
    "pdks",
    ".github",
    # Files included in other rst files.
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = 'CACE Documentation'
html_theme = 'furo'
html_static_path = ['_static']

# Auto-generated header anchors.
# https://myst-parser.readthedocs.io/en/stable/syntax/optional.html#syntax-header-anchors
myst_heading_anchors = 2
