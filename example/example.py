'''
Created on Jul 22, 2010

@author: shen
'''

from sapphire import sapphire
import re

if __name__ == '__main__':
    sph = sapphire()
    groups = sph.getAllGroups()
    for k, v in groups.items():
        if re.match('^BPM', k):
            print v
