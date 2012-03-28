#!/usr/bin/env python

import os

from pkg_resources import resource_string, resource_exists, resource_filename
from pvlist import vsr_pvlist

def has(resname):
    """
    check if resource exists.

    ${HOME}/.hla will be checked first, then the installed global settings.
    """
    # check HOME directory first
    if os.path.exists(os.path.join(os.getenv("HOME"), ".hla", resname)):
        return True
    else:
        return resource_exists(__name__, resname)

def filename(resname):
    """
    returns the true filename for resource

    check ${HOME}/.hla first, then the installed global settings.
    """
    # check the HOME for personal config file
    prv_filename = os.path.join(os.getenv("HOME"), ".hla", resname)
    if os.path.exists(prv_filename):
        return prv_filename
    else:
        # use the config within distribution
        return resource_filename(__name__, resname)


