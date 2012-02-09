#!/usr/bin/env python

from pkg_resources import resource_string, resource_exists, resource_filename

from pvlist import vsr_pvlist

def has(resname):
    return resource_exists(__name__, resname)

def filename(resname):
    return resource_filename(__name__, resname)


