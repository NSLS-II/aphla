from copy import copy, deepcopy
import re
from math import *
import sys

from optparse import OptionParser

"""
Usage
python create_lt_db.py your_pv_list_file
"""

my_version = "0.2"
vowner = "virtual"
elem_id = 0
prop_id = 0

prev_elem = ''

def fail(emesg, retcode):
    print >>sys.stderr, "%s: ERROR: %s" % (sys.argv[0],emesg)
    sys.exit(retcode)

def create_db():
    print "CREATE DATABASE IF NOT EXISTS itemfinder;"
    print "DROP TABLE IF EXISTS itemfinder.property;"
    print "DROP TABLE IF EXISTS itemfinder.element;"

    print "CREATE TABLE  `itemfinder`.`element` ("
    print "  `id` int(10) unsigned NOT NULL auto_increment,"
    print "  `name` varchar(45) NOT NULL,"
    print "  `owner` varchar(45) NOT NULL,"
    print "  PRIMARY KEY  (`id`)"
    print ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"

    print "CREATE TABLE  `itemfinder`.`property` ("
    print "  `id` int(10) unsigned NOT NULL auto_increment,"
    print "  `element_id` int(10) unsigned NOT NULL,"
    print "  `property` varchar(45) NOT NULL,"
    print "  `value` varchar(45) default NULL,"
    print "  `owner` varchar(45) NOT NULL,"
    print "  PRIMARY KEY  (`id`),"
    print "  KEY `property_element` (`element_id`),"
    print "  KEY `property_name` (`property`),"
    print "  CONSTRAINT `property_element` FOREIGN KEY (`element_id`) REFERENCES `element` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION"
    print ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"

    print "USE itemfinder"

def insert_element(name, owner):
    global elem_id
    elem_id = elem_id + 1;
    print "INSERT INTO element (id,name,owner) VALUE ("+`elem_id`+",'"+name+"','"+owner+"');"
    return elem_id

def insert_property_begin(elem, name, owner, value):
    global prop_id
    prop_id = prop_id + 1
    print "INSERT INTO property (id,element_id,property,owner,value) VALUES ("+`prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')",

def insert_property(elem, name, owner, value):
    global prop_id
    prop_id = prop_id + 1
    print ",("+`prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')",

def insert_tag(elem, name, owner):
    global prop_id
    prop_id = prop_id + 1
    print ",("+`prop_id`+","+`elem`+",'"+name+"','"+owner+"',DEFAULT)",

def insert_property_end():
    print ";"

# for virtual accelerator pv channel information
def do_insert(itemname, **kw):
    attrs = {}
    params = dict(attrs)
    params.update(kw)
    first = True

    cid = insert_element(itemname,vowner)
    for k, v in params.items():
        if first:
            insert_property_begin(cid,k,vowner,v)
            first = False
        else:
            insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
            ## insert_property(cid,k,vowner,v)
    insert_property_end()

def get_facility_from_pv(pvname):
    if pvname.startswith('SR'):
        return 'storage ring'
    elif pvname.startswith('LI'):
        return 'linac'
    elif pvname.startswith('BS'):
        return 'booster'

    return 'unknow'

def get_sub_sys_from_pv(pvname):
    pvfields = pvname.split(':')
    cell = pvfields[1][:3]
    gird = pvfields[2][:3]
    return cell, gird

# analysis a pv string reading from pv list file
# here we assume a pv name has following name convention:
# SR:C01-BI:G02A<BPM:0>Pos:X
def insert_items(attrs):
    modelIndex = attrs[0]
    pvRB = attrs[1]
    pvSP = attrs[2]
    phyName = attrs[3]
    length = attrs[4]
    position = attrs[5]
    group = attrs[6]

    if pvSP != 'NULL':
        facility = get_facility_from_pv(pvRB)
        cell, girder = get_sub_sys_from_pv(pvRB)
        do_insert(phyName, \
                  index = modelIndex, \
                  setpoint = pvSP, \
                  readback = pvRB, \
                  cell = cell, \
                  girder = girder, \
                  length = length, \
                  position = position,\
                  group = group)
    else:
        facility = get_facility_from_pv(pvSP)
        cell, girder = get_sub_sys_from_pv(pvRB)
        if group == 'BPM' or group == 'TUNE':
            hori = pvRB[:-1] + 'X'
            vert = pvRB[:-1] + 'Y'

            do_insert(phyName, \
                      index = modelIndex, \
                      horizontal = hori, \
                      vertical = vert, \
                      cell = cell, \
                      girder = girder, \
                      length = length, \
                      position = position,\
                      group = group )

   
def main(config):
    """The main procedure.

    parse the command-line options and perform the command
    """
    create_db()
    try:
        pv_file = open(config, 'r')
        lines = pv_file.readlines()
        for line in lines:
            line = line.strip()
            # Make sure line is not empty or commented out
            if line.startswith('!') or line.startswith('#') or len(line) == 0:
                pass
            else:
                attrs = line.split()
                global prev_elem
                if attrs[3] != prev_elem:
                    insert_items(attrs)
                else:
                    pass
                prev_elem = attrs[3]
    except IOError:
        print "I/O error({0}): {1}".format(errno, strerror)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise
    finally:
        pv_file.close()

if __name__ == "__main__":
    config = 'lat_conf_table.txt'
    if len(sys.argv) > 1:
        config = sys.argv[1]

    main(config)
