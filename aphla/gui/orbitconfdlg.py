# config dialog for orbit display
"""
"""

import os
import json

class OrbitPlotConfig(object):
    def __init__(self, dirname, filename):
        self.data = {}
        if dirname is None:
            #print "Using file:", filename
            fp = open(filename, 'r')
        else:
            fp = open(os.path.join(dirname, filename), 'r')
        #json.dump({'bpmx': [1,2,3]},
        self.data.update(json.load(fp))
        fp.close()
        #else:
        #    print "# No local version of ", conf
        #print self.data.keys(), len(self.data['bpmx']), len(self.data['bpmy'])
        pass
       

#obt = OrbitPlotConfig('/home/lyyang/.hla', 'nsls2_sr_orbit.json')

#if __name__ == "__main__":
    

