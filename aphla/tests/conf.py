#!/usr/bin/env python

import sys, os, time
import cothread


def wait_for_svr(val = [0], newval = 2):
    wt = 0
    while True:
        if caget('SVR:LOCKED') in val:
            caput('SVR:LOCKED', newval, wait=True)
            if wt > 0: print ''
            break
        if wt == 0: sys.stdout.write("\nWaiting for SVR:LOCKED released ")
        else: sys.stdout.write('.'),
        sys.stdout.flush()
        wt = wt + 1
        time.sleep(30)
    pass

def reset_svr(val = 0):
    caput('SVR:LOCKED', val, wait=True)


def hg_parent_rev():
    import commands
    stat, out = commands.getstatusoutput("hg summary")
    if stat == 0:
        for s in out.split('\n'):
            if s[:7] == 'parent:':
                return int(s.split(":")[1])
    return 0
