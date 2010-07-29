'''
Created on Jul 22, 2010

@author: shen
'''

from seasail import seasail
import re

if __name__ == '__main__':
    sph = sapphire()
    groups = sph.getAllGroups()
    print groups
    
    groupMembers, memberPos = sph.getMembers('BPM')
#    print groupMembers
#    print memberPos

    print sph.getLocation('BPM')
#    print sph.getChannels(group='BPM', type='xavg')
#    print sph.getChannels(group='BPM', type='yAvg')
#    print sph.getChannels(group='BPM', type='xTBT')
#    print sph.getChannels(group='BPM', type='yTBT')
#    print sph.getChannels(group='QUAD', type='SP')
#    print sph.getChannels(group='QUAD', type='RB')
    
    
    print sph.getLocation('TRIMX')
    print sph.getChannels(group='TRIMX', type='SP')
    print sph.getChannels(group='TRIMX', type='RB')

    print sph.getChannels(group='TRIMY', type='SP')
    print sph.getChannels(group='TRIMY', type='RB')

#    for k, v in groups.items():
#        if re.match('^BPM', k):
#            print v
    
#    spg.getChannels()
#    machines = sph.getMachine()
#    for k, v in machines.items():
#        print k
