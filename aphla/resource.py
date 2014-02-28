"""
Resource Management
--------------------
"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import os

from pkg_resources import resource_string, resource_exists, resource_filename
#from pvlist import vsr_pvlist

def has(resname):
    """
    check if resource exists.

    ${HOME}/.aphla will be checked first, then the installed global settings.
    """
    # check HOME directory first
    if os.path.exists(os.path.join(os.getenv("HOME"), ".aphla", resname)):
        return True
    else:
        return resource_exists(__name__, resname)

def getResource(resname, loc = None):
    """
    returns the true filename for resource

    check ${HOME}/.aphla first, then the installed global settings.
    """
    # check the HOME for personal config file
    prv_filename = os.path.join(os.getenv("HOME"), ".aphla", resname)
    if os.path.exists(prv_filename):
        return prv_filename
    elif loc and resource_exists(loc, resname):
        # use the config within distribution
        return resource_filename(loc, resname)
    else:
        return None

def filename(resname):
    """
    returns the true filename for resource

    check ${HOME}/.aphla first, then the installed global settings.
    """
    # check the HOME for personal config file
    prv_filename = os.path.join(os.getenv("HOME"), ".aphla", resname)
    if os.path.exists(prv_filename):
        return prv_filename
    else:
        # use the config within distribution
        return resource_filename(__name__, resname)

def inHome(resname):
    """
    check if resource is in user's HOME directory
    """
    prv_filename = os.path.join(os.getenv("HOME"), ".aphla", resname)
    if os.path.exists(prv_filename): 
        return True
    else: 
        return False
