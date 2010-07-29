#!/usr/bin/env python

"""This script read a table file, and convert it to a XML conf file"""

import sys, os
from time import gmtime, strftime

class buildConfig:
  def __init__(self, latfile):
      self.latfile = latfile
      self.comboid = ''
      self.prenode = ''
      self.comboseq = '  <comboseq id="SR">\n'

  def createBpmNode(self, rec):
      node = '       <group>\n'
      ## node += '          <group type="telem"  id="%s" />\n' % rec[1]
      ## node += '          <group type="tgroup" id="%s" />\n' % rec[4][:-1]
      ## node += '          <group type="type"   id="%s" />\n' % rec[7][:-1]
      node += '          <group id="%s" />\n' % rec[6]
      node += '       </group>\n'

      node += '       <attributes>\n'
      node += '          <align x="0.0" y="0.0" z="0.0" pitch="0" yaw="0" roll="0"/>\n'
      node += '          <aperture shape="0" x=""/>\n'
      node += '       </attributes>\n'

      node += '       <channelsuite name="bpmsuite">\n'

      node += '          <channel handle="xAvg" signal="%s" settable="false"/>\n' \
              % (rec[1].replace('<', '&lt;')).replace('>', '&gt;')
      node += '          <channel handle="yAvg" signal="%sY" settable="false"/>\n' \
              % (rec[1][:-1].replace('<', '&lt;')).replace('>', '&gt;')
      node += '          <channel handle="xTBT" signal="" settable="false"/>\n'
      node += '          <channel handle="yTBT" signal="" settable="false"/>\n'
      node += '       </channelsuite>\n'

      return node

  def createCavNode(self, rec):
      node = '       <group>\n'
      ## node += '          <group type="telem"  id="%s" />\n' % rec[1]
      ## node += '          <group type="tgroup" id="%s" />\n' % rec[4][:-1]
      ## node += '          <group type="type"   id="%s" />\n' % rec[7][:-1]
      node += '          <group id="%s" />\n' % rec[6]
      node += '       </group>\n'

      node += '       <attributes>\n'
      node += '          <align x="0.0" y="0.0" z="0.0" pitch="0" yaw="0" roll="0"/>\n'
      node += '          <aperture shape="0" x=""/>\n'
      node += '       </attributes>\n'

      node += '       <channelsuite name="rfsuite">\n'

      voltSP = ''
      voltRB = ''
      freqSP = ''
      freqRB = ''  
      if rec[3] == 'RFFREQ':
          freqSP = (rec[2].replace('<', '&lt;')).replace('>', '&gt;')
          freqRB = (rec[1].replace('<', '&lt;')).replace('>', '&gt;')
          voltSP = freqSP.replace('Freq', 'Volt')
          voltRB = freqRB.replace('Freq', 'Volt')
      elif rec[3] == 'RFVOLT':
          voltSP = (rec[2].replace('<', '&lt;')).replace('>', '&gt;')
          voltRB = (rec[1].replace('<', '&lt;')).replace('>', '&gt;')
          freqSP = voltSP.replace('Volt', 'Freq')
          freqRB = voltRB.replace('Volt', 'Freq')
      else:
          print 'RF format error.'
          return
          
      node += '          <channel handle="voltSP" signal="%s" settable="true"/>\n'  % voltSP
      node += '          <channel handle="voltRB" signal="%s" settable="false"/>\n' % voltRB
      node += '          <channel handle="fregSP" signal="%s" settable="true"/>\n'  % freqSP
      node += '          <channel handle="freqRB" signal="%s" settable="false"/>\n' % freqRB
      node += '       </channelsuite>\n'

      return node

  def createMagNode(self, rec):
      node = '       <group>\n'
      ## node += '          <group type="telem"  id="%s" />\n' % rec[1]
      ## node += '          <group type="tgroup" id="%s" />\n' % rec[4]
      ## node += '          <group type="type"   id="%s" />\n' % rec[7]
      node += '          <group id="%s" />\n' % rec[6]
      node += '       </group>\n'

      node += '       <attributes>\n'
      node += '          <magnet len="%s" polarity="" dfltMagFld=""/>\n' % rec[4]
      node += '          <align x="0.0" y="0.0" z="0.0" pitch="0" yaw="0" roll="0"/>\n'
      node += '          <aperture shape="0" x=""/>\n'
      node += '       </attributes>\n'

      node += '       <ps main="%s_PS"/>\n' % rec[3]

      node += '       <channelsuite name="magnetsuite">\n'

#Character Name 	Entity Reference 	Character Reference 	Numeric Reference
#Ampersand 	                &amp; 		& 						&#38;#38;
#Left angle bracket 	    &lt; 		< 						&#38;#60;
#Right angle bracket    	&gt; 		> 						&#62;
#Straight quotation mark 	&quot; 		" 						&#39;
#Apostrophe             	&apos; 		' 						&#34;
# ref: http://support.microsoft.com/kb/316063

      node += '          <channel handle="fieldRB" signal="%s" settable="false"/>\n' \
              % (rec[1].replace('<', '&lt;')).replace('>', '&gt;')
      node += '          <channel handle="fieldSP" signal="%s" settable="true"/>\n' \
              % (rec[2].replace('<', '&lt;')).replace('>', '&gt;')
      node += '       </channelsuite>\n'

      return node

  def addComboNode(self, comboid):
      self.comboseq += '    <sequence id="%s"/>\n' % comboid

  def getComboSeq(self):
      self.comboseq += '  </comboseq>\n'
      return self.comboseq

  def addNode(self, rec):
      typeName = ''
      body = ''
      seq = rec[3][-4:-1]
      if rec[6] == 'CAVITY':
          seq=rec[6]
          typeName = 'RF'
      if seq != self.comboid:
          if self.comboid != '':
              body += '  </sequence>\n'
          self.addComboNode(seq)
          body += '  <sequence type="%s" id="%s" len="">\n' % (typeName, seq)
          self.comboid = seq

      if rec[6] == 'BPM':
          body += '    <node type="%s" id="%s" pos="%s" len="%s" status="true">\n' \
                  % (rec[6], rec[3], rec[5], rec[4])
          body += self.createBpmNode(rec)
      elif rec[6] == 'CAVITY':
          body += '    <node type="%s" id="%s" pos="%s" len="%s" status="true">\n' \
                  % ('RF', rec[6], rec[5], rec[4])
          body += self.createCavNode(rec)
      else:
          body += '    <node type="%s" id="%s" pos="%s" len="%s" status="true">\n' \
                  % (rec[6], rec[3], rec[5], rec[4])
          body += self.createMagNode(rec)
      body += '    </node>\n'

      return body

  def getHead(self):
      ## t = strftime("%a %d %b %Y %H:%M:%S %Z", gmtime())
      t = strftime("%a, %d %b %Y, %H:%M:%S %Z")

      head = '<?xml version="1.0" encoding="UTF-8"?>\n'
      head += '<lattice system="NSLS2" ver="" date="%s">\n' % t
      head += '<!--pos is the end of an element along s direction -->\n'

      return head

  def getBody(self):
      latable = open(self.latfile, 'r').readlines()
      body = ''
      for line in latable:
          if not (line.startswith('!') or line.startswith('#')):
              rec = line.split()
              if rec[6] != self.prenode:
                  body += self.addNode(rec)
              self.prenode = rec[6]
      body += '  </sequence>\n'
      return body

  def getTail(self):
      return '</lattice>\n'

if __name__ == "__main__":
    write2File = False
    latfile = 'nsls2.xml'

    if len(sys.argv) < 2:
        print "Usage: %s lat_table.txt" % sys.argv[0]
        sys.exit(1)

    if len(sys.argv) > 2 and sys.argv[2] != '>' and sys.argv[2] != '>>':
        write2File = True
        latfile = sys.argv[2]

    gc = buildConfig(sys.argv[1])

    head = gc.getHead()
    body = gc.getBody()
    tail = gc.getTail()
    combo = gc.getComboSeq()

    if write2File:
        f = open(latfile, 'w')

        f.write(head)
        f.write(combo)
        f.write(body)
        f.write(tail)

        f.close()
    else:
        print head, body, tail

