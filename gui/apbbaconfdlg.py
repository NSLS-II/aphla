# config dialog for beam based alignment
"""
"""

import os
import json
from pkg_resources import resource_string

class BbaConfig(object):
    def __init__(self, dirname, filename):
        self.data = json.loads(
            resource_string(__name__, 'data/%s' % (filename,)))

        conf = os.path.join(dirname, filename)
        if os.path.exists(conf):
            #print "# Updating using local config"
            fp = open(conf, 'r')
            #json.dump({'bpmx': [1,2,3]},
            self.data.update(json.load(fp))
            fp.close()
        pass
       

