import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "BrainImageLibrary SDK"
author = "Ivan Cao-Berg"
copyright = "2026, Ivan Cao-Berg and the Brain Image Library Team"
release = "0.0.24"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_thebe",
]

thebe_config = {
    "repository_url": "https://github.com/brain-image-library/py-brain-sdk",
    "repository_branch": "main",
    "selector": "div.highlight",
}

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

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "_static/small_logo.png"
html_theme_options = {
    "dark_css_variables": {
        "color-brand-primary": "#4da6ff",
        "color-brand-content": "#4da6ff",
    },
    "light_css_variables": {
        "color-brand-primary": "#005fbf",
        "color-brand-content": "#005fbf",
    },
}
