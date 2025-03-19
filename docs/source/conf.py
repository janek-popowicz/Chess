# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Chess'
copyright = '2025, Janek Popowicz / Chopinpawns'
author = 'Janek Popowicz / Chopinpawns'
release = '1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys
sys.path.insert(0, os.path.abspath('../../'))  # Ustaw katalog główny projektu

extensions = [
    'sphinx.ext.autodoc',           # Generowanie dokumentacji z docstringów
    'sphinx.ext.napoleon',          # Obsługa docstringów w stylu Google i NumPy
    'sphinx.ext.autosummary',       # Automatyczne podsumowania modułów
    'sphinx_autodoc_typehints'      # Obsługa adnotacji typów
]

autosummary_generate = True
autodoc_member_order = 'bysource'
napoleon_google_docstring = True
napoleon_numpy_docstring = False

templates_path = ['_templates']
exclude_patterns = []

language = 'pl'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
