#!/usr/bin/env python2.7
"""
This script is used to run all HTML files in a directory through `htmlmin`.
"""

# Imports ######################################################################
import os
import htmlmin


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__date__ = "01/01/2014"
__copyright__ = "Avago Technologies, 2014"
__license__ = "Proprietary"
__version__ = "0.01"

# Globals ######################################################################
DEBUG = False
THIS_DIR = os.path.abspath(os.path.dirname(__file__))
HTML_DIR = os.path.abspath(os.path.join(THIS_DIR, "..", "mtik00.github.io"))


def slurp(path):
    """Return the text in a file."""
    with open(path, "rb") as fh:
        text = fh.read()

    return unicode(text)


def get_minimized_text(path):
    """Returns the minimized text in a file."""
    text = slurp(path)
    html = htmlmin.minify(text, remove_comments=True, remove_empty_space=True)
    return html


if __name__ == '__main__':
    for root, dirs, files in os.walk(HTML_DIR):
        for fname in [x for x in files if x.endswith(".html")]:
            html_file = os.path.join(root, fname)
            print "minimizing: ", html_file
            minimized_html = get_minimized_text(html_file)
            with open(html_file, "wb") as fh:
                fh.write(minimized_html)
