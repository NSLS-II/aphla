#!/usr/bin/env python

import os
import cadict

root={
    "nsls2" : "machine/nsls2"
}

# get the HLA root directory
pt = os.path.dirname(os.path.abspath(__file__))
xmlconf = "%s/../../%s/main.xml" % (pt, root['nsls2'])
print "Using conf file: ", xmlconf
ca = cadict.CADict(xmlconf)
#quad = ca.findGroup("QUAD")
#quadpv = ca.getChannels(quad[:5], mode="fieldRB")
#print ca.getGroups()
#print ca.getGroups('long')
