import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "brainimagelibrary"
author = "Ivan Cao-Berg"
copyright = "2026, Ivan Cao-Berg"
release = "0.0.17"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "private-members": False,
    "show-inheritance": True,
}

napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
