#!/usr/bin/env python

"""This script parses a XML conf file, and saves the information in a global place"""

#from lxml import etree

try:
    from lxml import etree
#    print("running with lxml.etree")
except ImportError:
    try:
        # Python 2.5
        import xml.etree.cElementTree as etree
#        print("running with cElementTree on Python 2.5+")
    except ImportError:
        try:
            # Python 2.5
            import xml.etree.ElementTree as etree
#            print("running with ElementTree on Python 2.5+")
        except ImportError:
            try:
                # normal cElementTree install
                import cElementTree as etree
#                print("running with cElementTree")
            except ImportError:
                try:
                    # normal ElementTree install
                    import elementtree.ElementTree as etree
#                    print("running with ElementTree")
                except ImportError:
                    raise
#                    print("Failed to import ElementTree from any known place")

import os

class parseConfig:
    def __init__(self):
        self.document = os.getenv('MACHINE')
        
        #print self.document
            
        self.machine = {}
        self.groups = {}
    
#    def getMachineSeq(self):
#        return self.machine
    
    def getGroups(self):
        return self.groups

    def parse(self):
#        facility = etree.parse(self.document, None, None)
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        self.facility = etree.parse(self.document, parser).getroot()
        
    def getAllMachines(self):
        # Use XPath to search tag 'id = acc_seq' instead of findall()
        expr = "/%s/comboseq" %self.facility.tag
        comboSeqs = self.facility.xpath(expr)
        
        return comboSeqs
#        for combo_seq in combo_seqs: 
#            com_seq_children = combo_seq.getchildren()
#        return self.facility.findall('comboseq')
    
    def getMachineSeq(self, machine):
        # Use XPath to search tag 'id = acc_seq' instead of findall()
        expr = "/%s/comboseq[@id='%s']" % (self.facility.tag, machine)
#        print expr
        comboSeq = self.facility.xpath(expr)

        if len(comboSeq) > 1:
            print 'More than 1 combo sequence defined. Use the first one'
#            return

        return comboSeq[0].getchildren()
#        return machine.findall('sequence')
    
    def getSeqIds(self, machine):
        sequences = machine.findall('sequence')
        seqIds = []
        for seq in sequences:
            seqIds.append(seq.get('id'))
        
        return seqIds
    
    def buildElemSeq(self, sequences):
        for child in sequences:
            expr = "/%s/sequence[@id='%s']" % (self.facility.tag, child.get('id'))
            #print expr, child.get('type')
            sequences = self.facility.xpath(expr)
            if len(sequences) > 1:
                print 'More than 1 sequence defined in the beam line for %s' % sequences[0].get('id')
                print 'Use the first found beam line'
            
            nodes = sequences[0].getchildren()
            for node in nodes:
                nodeDict = {}
                id = node.get('id')
                
                # add basic information
                nodeDict['id'] = [id]
                nodeDict['position'] = [node.get('pos')]
                nodeDict['length'] = [node.get('len')]
                nodeDict['status'] = [node.get('status')]
                
                # add group information
                exprGroup = expr+"/node[@id='%s']/group/group" %(id)
#                print exprGroup, node.get('type')
                groups = self.facility.xpath(exprGroup)
                for group in groups:
                    groupId = group.get('id')
                    if self.groups.has_key(groupId):
                        self.groups[groupId].append(id)
                    else:
                        self.groups[groupId] = [id]
                    if nodeDict.has_key('group'):
                        nodeDict['group'].append(groupId)
                    else:
                        nodeDict['group'] = [groupId]
                
                # add channel information
                exprChan = expr+"/node[@id='%s']/channelsuite/channel" %(id)
                channels = self.facility.xpath(exprChan)
                locDict = {}
                for chan in channels:
                    locDict[chan.get('handle')] = [chan.get('signal'), chan.get('settable')]
#                    if nodeDict.has_key('channel'):
#                        nodeDict['channel'].append(locDict)
#                    else:
#                        nodeDict['channel'] = [locDict]
                nodeDict['channel'] = locDict
                if self.machine.has_key(id):
                    self.machine[id].append(nodeDict)
                else:
                    self.machine[id] = [nodeDict]                

## if __name__ == '__main__':
##     import sys
##     import re
    
##     if len(sys.argv) > 1:
##         config = sys.argv[1]
    
##     pc = parseConfig()
##     pc.parse()
    
##     # here is the interface how to select a machine
##     for machine in pc.getAllMachines():
##         print machine.get('id')
        
##     machineSeqs = pc.getMachineSeq(machine.get('id'))
## #    for machineSeq in machineSeqs:
## #        print machineSeq.get('id')
    
##     # The Machine ID should be selected by user
##     elemSeq = pc.buildElemSeq(machineSeqs)
    
##     groups = pc.groups
##     for k, v in groups.items():
##         print k
##         if re.match('^bpm', k):
##             print v

    
