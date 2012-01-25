# config dialog for orbit display
"""
"""

import os
import json
from pkg_resources import resource_string

class OrbitPlotConfig(object):
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
        #else:
        #    print "# No local version of ", conf
        #print self.data.keys(), len(self.data['bpmx']), len(self.data['bpmy'])
        pass
       

#obt = OrbitPlotConfig('/home/lyyang/.hla', 'nsls2_sr_orbit.json')

#if __name__ == "__main__":
    
#from aphlas.config import Config

