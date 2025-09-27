import datetime

import syntax_diagrams

project = "Syntax Diagrams"
copyright = f"{datetime.date.today().year}, Tamika Nomara"
author = "Tamika Nomara"
release = version = syntax_diagrams.__version__

del syntax_diagrams

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.githubpages",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autodoc",
    "sphinx_design",
    "sphinx_syntax",
]

templates_path = ["_templates"]
exclude_patterns = []

primary_domain = "py"
default_role = "py:obj"
autodoc_type_aliases = {"Element": "syntax_diagrams.Element"}
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "PIL": ("https://pillow.readthedocs.io/en/stable/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_extra_path = ["_extra/robots.txt"]
html_css_files = ["syntax-diagrams-ext.css"]
html_theme_options = {
    "source_repository": "https://github.com/taminomara/syntax-diagrams",
    "source_branch": "main",
    "source_directory": "docs/source",
}
