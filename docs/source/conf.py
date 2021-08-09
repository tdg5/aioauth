# -- Path setup --------------------------------------------------------------

from pathlib import Path

# Project root folder.
root = Path(__file__).parent.parent.parent

# Loads __version__ file.
about = {}
with open(root / "aioauth" / "__version__.py", "r") as f:
    exec(f.read(), about)

# -- Project information -----------------------------------------------------

project = about["__title__"]
author = about["__author__"]
release = about["__version__"]

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "m2r2",
    "sphinx_copybutton",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]


# Adds custom css file.
def setup(app):
    app.add_css_file("custom.css")


# -- Extra Configuration -----------------------------------------------------

# Order of docs.
autodoc_member_order = "bysource"

# Turn off typehints.
autodoc_typehints = "signature"

# Remove module names from class docs.
add_module_names = False

# Show only class docs.
autoclass_content = "both"
