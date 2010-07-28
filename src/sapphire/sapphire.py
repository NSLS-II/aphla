'''
Created on Jul 23, 2010

@author: shen
'''

#from sapphire.lattice import parse_config
from lattice import parse_config

import os
import re

class sapphire:
    def __init__(self):
        keys = os.environ.keys()
        for key in keys:
            if not re.search('MACHINE', key):
                os.environ['MACHINE']='/home/shen/nsls-ii/nsls2-hla/src/sapphire/lattice/nsls2.xml'
    
        print 'hahahhahahahahah'
        self.pc = parse_config.parseConfig()
        self.pc.parse()
        
        machine = self.pc.getAllMachines()
        machineSeqs = self.pc.getMachineSeq(machine[0].get('id'))

        self.pc.buildElemSeq(machineSeqs)
    
    def getAllGroups(self):
        return self.pc.groups
