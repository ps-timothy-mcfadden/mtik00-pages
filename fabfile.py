#!/usr/bin/env python2.7
"""
This script is used to control deployment of my static HTML site.
"""
# Imports ######################################################################
import os
import re
import time

import toml
from fabric.api import local, env, task
from fabric.colors import red
from fabric.context_managers import lcd
from fabric.utils import puts
from fabric.tasks import execute


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "08/03/2015"
__license__ = "MIT"

# Globals ######################################################################
MAIN_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.abspath(os.path.join(MAIN_DIR, "mtik00.github.io"))
BIN_DIR = os.path.abspath(os.path.join(MAIN_DIR, "bin"))
HTMLMIN = True
JSON_PRETTY = True


# Fabric environment setup #####################################################
env.colorize_errors = True
################################################################################


@task
def dev():
    """clean, make, minify w/ no html min"""
    global HTMLMIN, JSON_PRETTY
    HTMLMIN = False
    JSON_PRETTY = True
    execute(clean)
    execute(make)


@task
def pull():
    """Pull changes from both repositories"""
    with lcd(MAIN_DIR):
        local("git pull")

    with lcd(STATIC_DIR):
        local("git pull")


@task
def clean():
    """Removes all generated files in the static folder"""
    for root, dirs, files in os.walk(STATIC_DIR, topdown=False):

        # Keep the .git folder
        if re.search("\.git(\\\\|$)", root):
            continue

        for name in files:
            os.remove(os.path.join(root, name))

        for name in [x for x in dirs if x != ".git"]:
            os.rmdir(os.path.join(root, name))

    time.sleep(1)


@task
def build():
    """Builds the static files in mtik00.github.io"""
    site = os.path.join(MAIN_DIR, "site")
    with lcd(site):
        local('..\\bin\\hugo.exe -d="..\\mtik00.github.io"')

    # Crappy hack for cache-busting the JSON index file.
    config_toml = os.path.join(MAIN_DIR, "site", 'config.toml')
    parsed_toml = toml.loads(open(config_toml, 'rb').read())
    version = parsed_toml['params'].get('static_version')

    if not version:
        return

    json_file = os.path.join(MAIN_DIR, 'mtik00.github.io', 'js', 'lunr-search.js')
    text = open(json_file, 'rb').read()
    text = re.sub('var indexfile = "/js/lunr-index.json"', 'var indexfile = "/js/lunr-index.json%s"' % version, text)
    with open(json_file, 'wb') as fh:
        fh.write(text)


@task
def make():
    """Makes the search index and builds the static files"""
    with lcd(MAIN_DIR):
        params = []
        if JSON_PRETTY:
            params.append("--pretty")

        if params:
            local("python bin\\make-search-index.py %s" % ' '.join(params))
        else:
            local("python bin\\make-search-index.py")

        if local("git status site\static\js\lunr-index.json --porcelain", capture=True):
            local("git add site\static\js\lunr-index.json")
            local('git commit -m"change in index.json"')
            local('git push')
        else:
            puts(red("no changes in index.json detected"))

    execute(build)


@task
def makeall():
    """clean, make, and minify"""
    execute(clean)
    execute(make)


@task
def release():
    """Commits and pushes static files, if needed"""

    # Check for local changes that need to be pushed
    if re.search("ahead of .* by \d+ commit", local('git status', capture=True)):
        local("git push")

    with lcd(STATIC_DIR):
        if local('git status --porcelain', capture=True):
            local("git add --all .")
            local("git clean -df")
            local('git commit -am"new content"')
            local('git push')
        else:
            puts(red("No changes found in static files"))


@task
def deploy():
    """make and release"""
    execute(makeall)
    execute(release)
