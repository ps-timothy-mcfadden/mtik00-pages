#!/usr/bin/env python2.7
"""
This script is used to control deployment of my static HTML site.
"""
# Imports ######################################################################
import os
import re
import sys
from fabric.api import local, env, task, execute
from fabric.colors import red
from fabric.operations import sudo
from fabric.context_managers import cd
from fabric.utils import puts


# Metadata #####################################################################
__author__ = "Timothy McFadden"
__creationDate__ = "07/27/2015"
__license__ = "Proprietary"

# Globals ######################################################################
FORCE = False
CLONE_UPDATED = False
RE_DEPLOY_FUNCTION_NAME = re.compile("^deploy_.*")
NEED_PUSH = None
RESET = False  # Full reset on web server repo

MAIN_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.abspath(os.path.join(MAIN_DIR, "mtik00.github.io"))


# Fabric environment setup #####################################################
# env.hosts = ['timandjamie.com']
# env.key_filename = os.environ["AWS_PRIVATE_KEY"]
# env.user = "ubuntu"
env.colorize_errors = True
################################################################################


def _prep():
    """Prepares for a deployment."""
    # _porcelain()

    if not (NEED_PUSH or FORCE):
        print red("Nothing to deploy: use the 'force' task to override")
        sys.exit()

    execute(git_push)


def _need_push():
    """Returns True if the remote branch needs to be updated; False otherwise."""
    if local("git log --branches --not --remotes", capture=True):
        return True

    return False


@task
def make():
    local("python bin\\make-search-index.py")
    if local("git status site\static\js\lunr.index.json --porcelain", capture=True):
        local("git add site\static\js\lunr.index.json")
        local('git commit -m"change in index.json"')
    else:
        puts("no changes in index.json detected")

    local('cd site && ..\\bin\\hugo.exe -d="..\\mtik00.github.io"')
    with cd("mtik00.github.io"):
        if local('git status --porcelain', capture=True):
            local("git add --all .")
            local("git clean -df")
            local('git commit -am"new content"')
            local('git push')
        else:
            puts("No changes found")


@task
def _porcelain(cwd=MAIN_DIR):
    """Check to ensure there is nothing to do before push/deploy."""
    puts("checking %s" % cwd)
    with cd(cwd):
        return local("git status --porcelain", capture=True)


@task
def reset():
    """Full reset on web server repo"""
    global RESET
    RESET = True


@task
def force():
    """Force other tasks (must be first task)."""
    global FORCE
    FORCE = True


@task
def git_push():
    """Push the local repo to the remote"""
    global NEED_PUSH

    if FORCE or NEED_PUSH:
        local("git push")
        NEED_PUSH = False


@task
def deploy():
    """Deploy the entire project.

    :var bool force: Disregard any need to push or porcelain status
    """
    _prep()

    local("make-release")
    local("git add --all public_html")

    result = local("git status --porcelain", capture=True)
    if result:
        local("git commit -m\"committing public files\"")
        local("git push")

    with cd("/var/www/com.timandjamie-static"):
        if RESET:
            sudo("git fetch origin master")
            sudo("git reset --hard FETCH_HEAD")
            sudo("git clean -df")
            sudo("ln -fs /var/www/com.timandjamie/public_html/addressbook /var/www/com.timandjamie-static/public_html/addressbook")
        else:
            sudo("git pull")

        sudo("chmod -R 755 public_html")


# NEED_PUSH = _need_push()
