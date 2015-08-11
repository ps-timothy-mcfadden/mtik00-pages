#!/usr/bin/env python2.7
"""
This script is used to run all HTML files in a directory through `htmlmin`,
css files through `csscompressor`, and all js files through `slimit`.

CSS and JS files are fingerprinted, and the names are changed.  If
--max-inline-bytes is non-zero, CSS and JS files that are under this many bytes
will be inlined in HTML source.  Otherwise, the fingerprinted URL will be
inserted instead.
"""

# Imports ######################################################################
import os
import re
import htmlmin
import argparse
from slimit import minify
from csscompressor import compress
from hashlib import md5


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__date__ = "08/06/2015"
__license__ = "MIT"


# Globals ######################################################################
# This data structure holds files that should be fingerprinted, and a list of
# files where the URL exists (so we don't have to search every single file).
OTHER_FINGERPRINTS = {
    "/js/lunr-index.json": ["/js/lunr-search.js"]
}


def get_args():
    """Parse the command-line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--static-dir', help="The base directory to process", type=str, required=True)
    parser.add_argument("--no-fingerprint-nonmin", help="Don't fingerprint non-minimized content", dest="fingerprint_nonmin", action="store_false")
    parser.add_argument("--no-htmlmin", help="Don't minimize the final HTML", dest="do_htmlmin", action="store_false")
    parser.add_argument("--no-inline", help="Don't inline any files", dest="do_inline", action="store_false")
    parser.add_argument("--max-inline-bytes", help="All files smaller than this will be inlined", type=int, default=4096)
    parser.set_defaults(fingerprint_nonmin=True, do_htmlmin=True, do_inline=True)
    return parser.parse_args()


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


def fingerprint(data, number_of_chars=10):
    """Returns the first 10 characters hexdigest of the MD5 hash of the data.

    We truncate the hash because: a) we don't care about collisions; b) we
    don't need really long filenames to enable fingerprint-based-caching.
    """
    m = md5()
    m.update(data)
    return m.hexdigest()[0:number_of_chars]


def process_js(base_dir, fingerprint_nonminimized=True):
    """Searches the base_dir for all JavaScript files.  When found, the file
    may be minimized (if not already), and may be fingerprinted.
    """
    js_map = {}
    js_files = []

    # Find all of the JavaScript files
    for root, dirs, files in os.walk(base_dir):
        for fname in [x for x in files if x.endswith(".js")]:
            js_files.append(os.path.join(root, fname))

    # Test each file
    for js_file in js_files:
        text = slurp(js_file)
        dirname, fname = os.path.split(js_file)
        fbase, fext = os.path.splitext(fname)

        if is_minimized(js_file) and fingerprint_nonminimized:
            fprint = fingerprint(text)
        else:
            text = minify(text)
            fprint = fingerprint(text)

        new_fname = "%s-%s%s" % (fbase, fprint, fext)  # E.g. "test-12345.js"
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


def process_css(base_dir, fingerprint_nonminimized=True):
    """Searches the base_dir for all CSS files.  When found, the file
    may be minimized (if not already), and may be fingerprinted.
    """
    css_map = {}
    css_files = []

    for root, dirs, files in os.walk(base_dir):
        for fname in [x for x in files if x.endswith(".css") and (".min" not in x)]:
            css_files.append(os.path.join(root, fname))

    for css_file in css_files:
        text = slurp(css_file)
        dirname, fname = os.path.split(css_file)
        fbase, fext = os.path.splitext(fname)

        if is_minimized(css_file) and fingerprint_nonminimized:
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


def do_inline(new_map, max_bytes=None):
    """Returns True if we think you should inline the file, False otherwise."""
    max_bytes = MAX_INLINE_BYTES if max_bytes is None else max_bytes
    return (max_bytes and (new_map["size"] <= max_bytes))


def shortend_path(path):
    """Returns the path of a file truncated to the first /"""
    return os.path.join(os.path.split(os.path.split(path)[0])[1], os.path.split(path)[1])


def remap_css(text, css_map, html_file, unlink_files):
    """Remaps or inlines new CSS files."""
    for old, new in css_map.items():
        match = re.search("""(<link rel=.?stylesheet.? href=.+%s.*?>)""" % old, text)
        if not match:
            continue
        elif do_inline(new):
            print "inlining [%s] in [%s]" % (old, shortend_path(html_file))
            fname = os.path.splitext(os.path.split(old)[1])[0]
            new_css = """<style type="text/css" title="%s">%s</style>""" % (fname, slurp(new["path"]))
            text = text.replace(match.group(1), new_css)
            unlink_files.add(new["path"])
        else:
            print "subbing [%s] in [%s]" % (old, shortend_path(html_file))
            text = text.replace(old, new["url"])

    return text


def remap_js(text, js_map, html_file, unlink_files):
    """Remaps or inlines new JS files."""
    for old, new in js_map.items():
        skip_inline = False

        if old.endswith(".js"):
            match = re.search("""(<script type=.?text/javascript.*?%s.*?</script>)""" % old, text)
        elif old.endswith(".json"):
            match = re.search('"%s"' % old, text)
            skip_inline = True

        if not match:
            continue
        elif do_inline(new) and (not skip_inline):
            print "inlining [%s] in [%s]" % (old, shortend_path(html_file))
            fname = os.path.splitext(os.path.split(old)[1])[0]
            new_js = """<script type="text/javascript" title="%s">%s</script>""" % (fname, slurp(new["path"]))
            text = text.replace(match.group(1), new_js)
            unlink_files.add(new["path"])
        else:
            print "subbing [%s] in [%s]" % (old, shortend_path(html_file))
            text = text.replace(old, new["url"])

    return text


def process_html(base_dir, css_map, js_map, do_htmlmin=True):
    """Minimizes the HTML file, optionally replacing fingerprinted files and/or
    inlining them."""
    html_files = []
    unlink_files = set([])

    for root, dirs, files in os.walk(base_dir):
        for fname in [x for x in files if x.endswith(".html")]:
            html_files.append(os.path.join(root, fname))

    for html_file in html_files:
        text = slurp(html_file)
        text = remap_css(text, css_map, html_file, unlink_files)
        text = remap_js(text, js_map, html_file, unlink_files)

        if do_htmlmin:
            text = htmlmin.minify(text, remove_comments=True, remove_empty_space=False)

        with open(html_file, "wb") as fh:
            fh.write(text)

    for unlink_file in unlink_files:
        os.unlink(unlink_file)


def process_other_fingerprints(static_dir, fingerprints):
    """Process the fingerprints that need a bit more finesse than straight
    automatic.
    """
    for old, files in fingerprints.items():
        fpath = os.path.join(static_dir, *old.split("/"))
        if not os.path.exists(fpath):
            continue

        data = slurp(fpath)
        dirname, fname = os.path.split(fpath)
        fbase, fext = os.path.splitext(fname)

        fprint = fingerprint(data)
        new_fname = "%s-%s%s" % (fbase, fprint, fext)
        new_path = os.path.join(dirname, new_fname)
        new_url = new_path[len(static_dir):].replace("\\", "/")

        os.rename(fpath, new_path)

        for file_ in files:
            new_file_path = os.path.join(static_dir, *file_.split("/"))
            text = slurp(new_file_path)
            if old in text:
                text = text.replace(old, new_url)

                with open(new_file_path, "wb") as fh:
                    fh.write(text)


if __name__ == '__main__':
    args = get_args()

    if not args.do_inline:
        MAX_INLINE_BYTES = 0
    else:
        MAX_INLINE_BYTES = args.max_inline_bytes

    process_other_fingerprints(args.static_dir, OTHER_FINGERPRINTS)
    css_map = process_css(args.static_dir, args.fingerprint_nonmin)
    js_map = process_js(args.static_dir, args.fingerprint_nonmin)
    process_html(args.static_dir, css_map, js_map, args.do_htmlmin)
