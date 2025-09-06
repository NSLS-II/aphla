from __future__ import print_function, division, absolute_import

"""
Resource Management
--------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import os
from importlib import import_module
from importlib.resources import files, as_file

#from pvlist import vsr_pvlist

def has(resname):
    """
    check if resource exists.

    ${HOME}/.aphla will be checked first, then the installed global settings.
    """
    # check HOME directory first
    home = os.path.join(os.path.expanduser("~"), ".aphla", resname)
    if os.path.exists(home):
        return True
    pkg_path = files(__name__) / resname
    # Consider both file and directory resources
    return pkg_path.is_file() or pkg_path.is_dir()

def getResource(resname, loc = None):
    """
    returns the true filename for resource

    check ${HOME}/.aphla first, then the installed global settings.
    """
    # check the HOME for personal config file
    prv_filename = os.path.join(os.path.expanduser("~"), ".aphla", resname)
    if os.path.exists(prv_filename):
        return prv_filename
    elif loc:
        # `loc` can be a package name or module object
        pkg = import_module(loc) if isinstance(loc, str) else loc
        pkg_item = files(pkg) / resname
        if pkg_item.is_file() or pkg_item.is_dir():
            # Ensure real filesystem path even if in a zip
            with as_file(pkg_item) as p:
                return str(p)
    else:
        return None


def filename(resname):
    """
    returns the true filename for resource

    check ${HOME}/.aphla first, then the installed global settings.
    """
    # check the HOME for personal config file
    prv_filename = os.path.join(os.path.expanduser("~"), ".aphla", resname)
    if os.path.exists(prv_filename):
        return prv_filename

    # use the config within distribution
    pkg_item = files(__name__) / resname
    if pkg_item.is_file() or pkg_item.is_dir():
        with as_file(pkg_item) as p:
            return str(p)
    raise FileNotFoundError(f"Resource not found: {resname!r} in package {__name__!r}")


def inHome(resname):
    """
    check if resource is in user's HOME directory
    """
    prv_filename = os.path.join(os.path.expanduser("~"), ".aphla", resname)
    if os.path.exists(prv_filename):
        return True
    else:
        return False
