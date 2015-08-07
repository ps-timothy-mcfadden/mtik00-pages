#!/usr/bin/env python2.7
"""
This script is used to run all HTML files in a directory through `htmlmin`,
css files through `csscompressor`, and all js files through `slimit`.

CSS and JS files are fingerprinted, and the names are changed.  If
MIN_INLINE_BYTES is non-zero, CSS and JS files that are under this many bytes
will be inlined in HTML source.  Otherwise, the fingerprinted URL will be
inserted instead.
"""

# Imports ######################################################################
import os
import re
import base64
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
MIN_INLINE_BYTES = 4097
FINGERPRINT_NONMIN = True


def slurp(path):
    """Return the text in a file."""
    with open(path, "rb") as fh:
        text = fh.read()

    return unicode(text)


def is_minimized(path):
    """Returns True if we think the script/css has already been minimized based
    on the filename; False otherwise.
    """
    _, fname = os.path.split(path)
    return (".min" in fname) or (".pack" in fname)


def fingerprint(data):
    """Returns the hexdigest of the MD5 hash of the data"""
    m = md5()
    m.update(data)
    return base64.urlsafe_b64encode(m.digest()[0:10])[:-2]


def process_js(base_dir):
    js_map = {}
    js_files = []
    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".js")]:
            js_files.append(os.path.join(root, fname))

    for js_file in js_files:
        text = slurp(js_file)
        dirname, fname = os.path.split(js_file)
        fbase, fext = os.path.splitext(fname)

        if is_minimized(js_file) and FINGERPRINT_NONMIN:
            fprint = fingerprint(text)
        else:
            text = minify(text)
            fprint = fingerprint(text)

        new_fname = "%s-%s%s" % (fbase, fprint, fext)
        new_path = os.path.join(dirname, new_fname)
        with open(new_path, "wb") as fh:
            fh.write(text)

        new_url = new_path[len(base_dir):].replace("\\", "/")
        old_url = js_file[len(base_dir):].replace("\\", "/")
        new_size = os.stat(new_path).st_size
        old_size = os.stat(js_file).st_size

        print "%s reduced by %0.2f%%" % (old_url, 100.0 * (old_size - new_size) / old_size)

        js_map[old_url] = {
            "url": new_url,
            "size": os.stat(new_path).st_size,
            "path": new_path
        }

        os.unlink(js_file)

    return js_map


def process_css(base_dir):
    """minfies CSS, and finger prints it."""
    css_map = {}
    css_files = []

    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".css") and (".min" not in x)]:
            css_files.append(os.path.join(root, fname))

    for css_file in css_files:
        text = slurp(css_file)
        dirname, fname = os.path.split(css_file)
        fbase, fext = os.path.splitext(fname)

        if is_minimized(css_file) and FINGERPRINT_NONMIN:
            fprint = fingerprint(text)
        else:
            text = compress(text)
            fprint = fingerprint(text)

        new_fname = "%s-%s%s" % (fbase, fprint, fext)
        new_path = os.path.join(dirname, new_fname)
        with open(new_path, "wb") as fh:
            fh.write(text)

        new_url = new_path[len(base_dir):].replace("\\", "/")
        old_url = css_file[len(base_dir):].replace("\\", "/")
        new_size = os.stat(new_path).st_size
        old_size = os.stat(css_file).st_size

        print "%s reduced by %0.2f%%" % (old_url, 100.0 * (old_size - new_size) / old_size)

        css_map[old_url] = {
            "url": new_url,
            "size": new_size,
            "path": new_path
        }

        os.unlink(css_file)

    return css_map


def process_html(base_dir, css_map, js_map):
    """Minimizes the HTML file, optionally replacing fingerprinted files and/or
    inlining them."""
    def fpath(path):
        """Returns the path of a file truncated to the first /"""
        return os.path.join(os.path.split(os.path.split(path)[0])[1], os.path.split(path)[1])

    html_files = []
    unlink_files = set([])

    for root, dirs, files in os.walk(htmldir):
        for fname in [x for x in files if x.endswith(".html")]:
            html_files.append(os.path.join(root, fname))

    for html_file in html_files:
        text = slurp(html_file)

        for old, new in css_map.items():
            if old not in text:
                # print "...can't find it [%s] in [%s]" % (old, fpath(html_file))
                continue
            elif MIN_INLINE_BYTES and (new["size"] < MIN_INLINE_BYTES):
                print "inlining [%s] in [%s]" % (old, fpath(html_file))
                fname = os.path.splitext(os.path.split(old)[1])[0]
                # old_sub = "<link href='%s' rel='stylesheet' type='text/css'>" % old
                old_sub = '<link rel="stylesheet" href="%s">' % old
                sub = '<style type="text/css" title="%s"\>%s\</style>' % (fname, slurp(new["path"]))
                text = re.sub(old_sub, sub, text)
                unlink_files.add(new["path"])
            else:
                print "subbing [%s] in [%s]" % (old, fpath(html_file))
                text = re.sub(old, new["url"], text)

        for old, new in js_map.items():
            if MIN_INLINE_BYTES and (new["size"] < MIN_INLINE_BYTES):
                print "inlining [%s] in [%s]" % (old, fpath(html_file))
                sub = '\n<script type="text/javascript" title="%s">%s</script>\n' % (new["url"], slurp(new["path"]))
                old_sub = '<script type="text/javascript" async src="%s"></script>' % old
                text = re.sub(old_sub, sub, text)
                unlink_files.add(new["path"])

            text = re.sub(old, new["url"], text)

        # text = htmlmin.minify(text, remove_comments=True, remove_empty_space=False)

        with open(html_file, "wb") as fh:
            fh.write(text)

    for unlink_file in unlink_files:
        os.unlink(unlink_file)

if __name__ == '__main__':
    import sys
    htmldir = sys.argv[1]
    css_map = process_css(htmldir)
    js_map = process_js(htmldir)
    process_html(htmldir, css_map, js_map)
