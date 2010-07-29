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
    
        self.pc = parse_config.parseConfig()
        self.pc.parse()
        
        machine = self.pc.getAllMachines()
        machineSeqs = self.pc.getMachineSeq(machine[0].get('id'))

        self.pc.buildElemSeq(machineSeqs)
        
        self.defaults = {}
        
        self.chanSigType = {'xavg': 'xAvg',   \
                           'yavg': 'yAvg',    \
                           'xtbt': 'xTBT',    \
                           'ytbt': 'yTBT',    \
                           'sp':   'fieldSP', \
                           'rb':   'fieldRB'
                           }
    
    def getAllGroups(self):
        groupName = []
        for k, v in self.pc.groups.items():
            groupName.append(k)
        return groupName
    
    def getMembers(self, group):
        members = []
        s = []
        for k, vs in self.pc.groups.items():
            if re.match(group, k):
                for v in vs:
                    members.append(v)
                    try:
                        s.append(self.pc.machine[v][0]['position'][0])
                    except:
                        print 'Group [%s] does not have member [%s]' %(group, v)
                        raise
        return members, s
    
    def getMemberStatus(self, group):
        status = []
        members, s = self.getMembers(group)
        for member in members:
            try:
                status.append(self.pc.machine[member][0]['status'][0])
            except:
                print 'Group [%s] does not have member [%s]' %(group, member)
                raise
        return status
    
    def getLocation(self, group):
#        s = []
#        members, s = self.getMembers(group)
        return self.getMembers(group)[1]
    
    def getChannels(self, **kw):
        params = dict(self.defaults)
        params.update(kw)
        group = ''
        items = ''
        
        try:
            group = params['group']
            items = params['items']
        except:
            pass
        
        if group == '' and items == '':
            print 'Your have to specify either group name or items list'
            return #raise
        
#        for k, vs in self.pc.groups.items():
#            if re.match(k, group):
#                print group
        
        if items == '':
            key = group
            if group.find('BPM') != -1:
                key = 'BPM'
            items = self.getMembers(key)[0]

        channs = []
        for item in items:
            itemAttrs = self.pc.machine[item][0]
#            print itemAttrs
            key = self.chanSigType[str.lower(params['type'])]
            channs.append(itemAttrs['channel'][key][0])
        
        return channs
    