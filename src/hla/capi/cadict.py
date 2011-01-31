#!/usr/bin/env python

from xml.dom import minidom
import sys, copy

"""A dictionary for channel access info of all elements.

It flatten XML configure file, organizes lattice element and channel info
into a list"""

class CAElement:
    def __init__(self, name = "", elemtype = ""):
        self.name = name
        self.type = elemtype
        self.pos = 0.0
        self.length = 0.0
        self.ca = []
        self.handle = []
        self.sequence = []
        self.group = []

    def addCa(channel, handle, sequence = []):
        self.ca.append(channel)
        self.handle.append(handle)
        self.sequence = [ s for s in sequence]

class CADict:
    def __init__(self, mainxml):
        self.input = mainxml
        self.elements = []
        dom = minidom.parse(self.input)
        
        elem = CAElement()

        self.findElementCa(dom.childNodes, elem)
    
    def elementExists(self, element):
        for elem in self.elements:
            if elem.name == element: return True
        return False

    def findElement(self, elemname):
        for elem in self.elements:
            if elem.name == elemname: return elem
        return None

    def findElementCa(self, nodeList, elem):
        #print "start"
        for subnode in nodeList:
            if subnode.nodeType == subnode.ELEMENT_NODE:
                if subnode.tagName in ["lattice", "sequence"]:
                    elem.sequence.append(subnode.getAttribute("id"))
                if subnode.tagName == "node":
                    elem.name     = subnode.getAttribute("id")
                    elem.elemtype = subnode.getAttribute("type")
                    elem.pos      = float(subnode.getAttribute("pos"))
                    elem.length   = float(subnode.getAttribute("len"))
                elif subnode.tagName == "channel":
                    elem.ca     = [subnode.getAttribute("signal")]
                    elem.handle = [subnode.getAttribute("handle")]
                    if not self.elementExists(elem.name):
                        self.elements.append(CAElement())
                        #print "Exists:", elem.name, len(self.elements)
                        self.elements[-1].name     = elem.name
                        self.elements[-1].elemtype = elem.elemtype
                        self.elements[-1].pos      = elem.pos
                        self.elements[-1].length   = elem.length
                        self.elements[-1].ca       = [elem.ca[0]]
                        self.elements[-1].handle   = [elem.handle[0]]
                        self.elements[-1].sequence = elem.sequence[:]
                    else:
                        elp = self.findElement(elem.name)
                        elp.ca.append(elem.ca[0])
                        elp.handle.append(elem.handle[0])
                        # did not check if same element appears with difference sequence
                self.findElementCa(subnode.childNodes, elem)
                if subnode.tagName in ["lattice", "sequence"]:
                    elem.sequence.pop(-1)
                    #print elem.sequence.pop(-1), subnode.getAttribute("id")
            elif subnode.nodeType == subnode.TEXT_NODE:
                #print "text:", subnode.data
                pass

    def __repr__(self):
        s = ""
        for elem in self.elements:
            for seq in elem.sequence:
                s = s + "%s/" % seq

            s = s + "%s %12.6f %f  : %7s\n" % (elem.name, elem.pos, elem.length, elem.elemtype)
            for i in range(len(elem.handle)):
                s = s + "    %s/%s \n" % (elem.ca[i], elem.handle[i])
            s = s +'\n'
        return s

if __name__ == "__main__":
    ca = CADict("/home/lyyang/devel/nsls2-hla/machine/nsls2/main.xml")
    print ca

