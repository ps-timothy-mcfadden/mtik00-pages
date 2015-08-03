#!/usr/bin/env python2.7
"""
This script is used to control deployment of my static HTML site.
"""
# Imports ######################################################################
import os
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


# Fabric environment setup #####################################################
env.colorize_errors = True
################################################################################


@task
def pull():
    """Pull changes from both repositories"""
    with lcd(MAIN_DIR):
        local("git pull")

    with lcd(STATIC_DIR):
        local("git pull")


@task
def build():
    """Builds the static files in mtik00.github.io"""
    site = os.path.join(MAIN_DIR, "site")
    with lcd(site):
        local('..\\bin\\hugo.exe -d="..\\mtik00.github.io"')


@task
def make():
    with lcd(MAIN_DIR):
        local("python bin\\make-search-index.py")

        if local("git status site\static\js\lunr.index.json --porcelain", capture=True):
            local("git add site\static\js\lunr.index.json")
            local('git commit -m"change in index.json"')
        else:
            puts(red("no changes in index.json detected"))

    execute(build)


@task
def release():
    """Commits and pushes static files, if needed"""
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
    execute(make)
    execute(release)
