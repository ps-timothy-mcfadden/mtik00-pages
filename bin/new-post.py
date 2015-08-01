#!/usr/bin/env python2.7
"""
This script is used to create a new Hugo post and set some of the front matter.

It's purposefully built for my particular usage of Hugo (I have my content in
"site/content/YYYY", where YYYY is the current year).  This is simply to
organize the content.  I use a permalink of "/:year/:month/:slug/" to organize
the generated static files.

This script serves the following purposes:
    1.  Disassociate a posts Title with it's filename
    2.  Keep posts organized according to year created
    3.  Keep the slugs consistent (which leads to consistency in static HTML URLs)

NOTE: Only TOML format is supported.
"""

# Imports ######################################################################
import os
import re
import sys
import time
import subprocess


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "07/29/2015"
__license__ = "MIT"

# Globals ######################################################################
DEBUG = False
BIN_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = os.path.join(BIN_DIR, "..")
CONTENT_DIR = os.path.join(BASE_DIR, "site", "content")


def ex(command, cwd=None):
    """Execute a command and return the output.  This will raise an Exception if
    the return code is non-zero.
    """
    shell = type(command) is not list

    p = subprocess.Popen(command, shell=shell, cwd=cwd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    output, _ = p.communicate()

    if p.returncode:
        raise Exception("command failed: %s" % output)

    return output


def get_title_and_filename(arguments):
    """Ask the user for a title, or get it from arguments.

    Returns the title, and a decent name for the filename to be eventually
    created.
    """
    if len(arguments) == 1:
        title = raw_input("Enter the title of the post: ")
        if not title:
            sys.exit(1)
    else:
        title = " ".join(arguments[1:])

    # Convert the title into a nicely formatted filename
    filename = re.sub("[,:;*\\/\.!\(\)\[\]\{\}\"$\s'<>]", "-", title.strip().lower())
    filename = re.sub("-+", "-", filename)
    if filename.endswith("-"):
        filename = filename[:-1]

    return (title, filename)


def create_post(filename):
    """Call Hugo's `new` command to create the post.  The post will be created
    in a subfolder according to the current year.

    Returns the absolute path to the file that Hugo probably created.
    """
    year = time.strftime("%Y", time.localtime())
    cmd = '''hugo new "{0}" --source="site" --config="site/config.toml"'''
    post_subpath = "posts\{0}\{1}.md".format(year, filename)
    post_dir = os.path.join(CONTENT_DIR, os.path.dirname(post_subpath))
    post_path = os.path.join(post_dir, "%s.md" % filename)

    if not os.path.isdir(post_dir):
        os.makedirs(post_dir)

    cmd = cmd.format(post_subpath)

    print ex(cmd, BASE_DIR)

    return os.path.abspath(post_path)


def set_front_matter(path, title, filename):
    """Modify the front matter of a pre-existing file.

    Insert the slug and the title.  I haven't found a way to get Hugo to create
    the new content with "dynamic" fields (those not already in an archetype).
    """
    with open(path, "rb") as fh:
        lines = fh.read().split("\n")

    with open(path, "wb") as fh:
        in_header = False
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("+++") and not in_header:
                in_header = True
            elif line.startswith("+++") and in_header:
                line = "%s\n%s" % (
                    'slug = "%s"' % filename,
                    line)
            elif line.startswith("title"):
                line = 'title = "%s"' % title

            fh.write("%s\n" % line)


if __name__ == '__main__':
    (title, filename) = get_title_and_filename(sys.argv)
    path = create_post(filename)
    set_front_matter(path, title, filename)
