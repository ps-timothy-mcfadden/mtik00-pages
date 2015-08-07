#!/usr/bin/env python2.7
"""
This script is used to run all HTML files in a directory through `htmlmin`,
css files through `csscompressor`, and all js files through `slimit`.

.... TBD: asset fingerprinting
"""

# Imports ######################################################################
import os
import re
import htmlmin
from slimit import minify
from csscompressor import compress
from hashlib import md5


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__date__ = "08/06/2015"
__license__ = "MIT"


# Globals ######################################################################
DEBUG = False


def slurp(path):
    """Return the text in a file."""
    with open(path, "rb") as fh:
        text = fh.read()

    return unicode(text)


def process_js(base_dir):
    js_map = {}
    js_files = []
    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".js")]:
            js_files.append(os.path.join(root, fname))

    for js_file in js_files:
        text = slurp(js_file)
        text = minify(text)
        m = md5()
        m.update(text)

        dirname, fname = os.path.split(js_file)
        fbase, fext = os.path.splitext(fname)

        new_fname = "%s-%s%s" % (fbase, m.hexdigest(), fext)
        print js_file, new_fname
        new_path = os.path.join(dirname, new_fname)
        with open(new_path, "wb") as fh:
            fh.write(text)

        new_url = new_path[len(base_dir):].replace("\\", "/")
        old_url = js_file[len(base_dir):].replace("\\", "/")
        js_map[old_url] = new_url

        os.unlink(js_file)

    return js_map


def process_css(base_dir):
    """minfies CSS, and finger prints it."""
    css_map = {}
    css_files = []
    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".css")]:
            css_files.append(os.path.join(root, fname))

    for css_file in css_files:
        css_text = slurp(css_file)
        text = compress(css_text)
        m = md5()
        m.update(text)

        dirname, fname = os.path.split(css_file)
        fbase, fext = os.path.splitext(fname)

        new_fname = "%s-%s%s" % (fbase, m.hexdigest(), fext)
        print css_file, new_fname
        new_path = os.path.join(dirname, new_fname)
        with open(new_path, "wb") as fh:
            fh.write(text)

        new_url = new_path[len(base_dir):].replace("\\", "/")
        old_url = css_file[len(base_dir):].replace("\\", "/")
        css_map[old_url] = new_url

        os.unlink(css_file)

    return css_map


def process_html(base_dir, css_map, js_map):
    """Minimizes the HTML file."""
    html_files = []
    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".html")]:
            html_files.append(os.path.join(root, fname))

    for html_file in html_files:
        text = slurp(html_file)

        for old, new in css_map.items():
            text = re.sub(old, new, text)

        for old, new in js_map.items():
            text = re.sub(old, new, text)

        # html = htmlmin.minify(text, remove_comments=True, remove_empty_space=True)

        with open(html_file, "wb") as fh:
            fh.write(text)


if __name__ == '__main__':
    import sys
    htmldir = sys.argv[1]
    css_map = process_css(htmldir)
    js_map = process_js(htmldir)
    process_html(htmldir, css_map, js_map)
