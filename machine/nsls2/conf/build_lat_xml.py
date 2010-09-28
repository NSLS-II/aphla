#!/usr/bin/env python

"""This script read a table file, and convert it to a XML conf file"""

import sys, os

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Usage: %s lat_table.txt" % sys.argv[0]
        sys.exit(1)

    # write XML head
    print '<?xml version="1.0" encoding="UTF-8">\n' \
        '<lattice name="NSLS2">'
    latable = open(sys.argv[1], 'r').readlines()
    for line in latable:
        rec = line.split()
        print '  <element>'
        print '    <name>%s</name>' % rec[6]
        print '    <group>%s</group>' % rec[1]
        print '    <group>%s</group>' % rec[4]
        print '    <group>%s</group>' % rec[7]
        print '    <length>%s</length>' % rec[8]
        print '    <s_begin>%s</s_begin>' % '0'
        print '    <s_end>%s</s_end>' % rec[5]
        print '    <s_end>%s</s_end>' % rec[9]
        print '    <channel>%s</channel>' % rec[2]
        print '    <channel>%s</channel>' % rec[3]
        print '  </element>'
    # read table and output
    print '</lattice>'
