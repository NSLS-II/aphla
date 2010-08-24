#!/usr/bin/env python
"""
This script generates a sql script, which assumes MySQL as underneath RDBMS.

It reads a configuration file, and load all information into IRMIS database.
This is for item finder pvService, and the temporary database name is itemfinder.
It consists of 2 temporary tables: element, and property.
The table depends on the configuration format, and current supported format is as below:
#index   read back                       set point                      phys name      len[m]   s[m]    group name
3242    SR:C30-MG:G01A<HCM:H1>Fld-RB    SR:C30-MG:G01A<HCM:H1>Fld-SP    CFXH1G1C30A    0.044    787.793    TRIMX
3243    SR:C30-MG:G01A<VCM:H1>Fld-RB    SR:C30-MG:G01A<VCM:H1>Fld-SP    CFYH1G1C30A    0.044    787.793    TRIMY
 ...

Essentially, the information in the configuration is from a virtual accelerator, which uses Tracy-III 
as simulation engine. The index is the sequence number of an element in the simulation code, and channel
name follows name convention. The physics name, length, and position are from lattice deck. The group name
identifies this element belongs to which group, which is very preliminary so far.  

Each time, when to load a new configuration, it deletes existing tables, and create new tables. 
This has to be improved later to support multiple version decks.

usage: python build_if_db.py lat_conf_table.txt rdb_host rdb_user rdb_pw

@author:    GS, Aug 20, 2010
@copyright: National Synchrotron Light Source II
            Brookhaven National Laboratory, Upton, NY, 11973
@license:   TBD
"""
import os
import sys
import MySQLdb

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

__author__ = 'Guobao Shen (shengb@bnl.gov)'

class build_if_db:
    def __init__(self, config, host='localhost', user='test' , pw='test_pw', db='itemfinder', port=3306):
        self.vowner = "virtual"
        self.elem_id = 0
        self.prop_id = 0
        self.prev_elem = ''
        self.host = host
        self.user = user
        self.pw = pw
        self.elem_id = 0
        self.prop_id = 0
        self.dbname = db
        self.port = port
        self.config = config
            
    def fail(self, emesg, retcode):
        print >>sys.stderr, "%s: ERROR: %s" % (sys.argv[0],emesg)
        sys.exit(retcode)
    
    def connect_if_db(self):
        try:
            self.db= MySQLdb.connect(host=self.host, user=self.user, passwd=self.pw, db=self.dbname, port=self.port)
            self.cursor= self.db.cursor()
        except:
            print ('wrong user name and password for database: ' + self.dbname)
            raise
    
    def clean_tables(self):
        # start with new tables;
        self.cursor.execute("delete from property;")
        self.cursor.execute("delete from element;")

    def insert_element(self, name, owner):
        self.elem_id = self.elem_id + 1;
#        print "INSERT INTO element (id,name,owner) VALUE ("+`self.elem_id`+",'"+name+"','"+owner+"');"
        cmd = "INSERT INTO element (id,name,owner) VALUE (%d, '%s', '%s');" %(self.elem_id, name, owner)
#        self.cursor.execute("INSERT INTO element (id,name,owner) VALUE (%d, '%s', '%s');" %(self.elem_id, name, owner))
#        print cmd
        self.cursor.execute(cmd)
        return self.elem_id
    
    def insert_property_begin(self, elem, name, owner, value):
        self.prop_id = self.prop_id + 1
        return "INSERT INTO property (id,element_id,property,owner,value) VALUES ("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')"    
#        print "INSERT INTO property (id,element_id,property,owner,value) VALUES ("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')",
    
    def insert_property(self, elem, name, owner, value):
        self.prop_id = self.prop_id + 1
        return ",("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')"
#        print ",("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"','"+value+"')",
    
    def insert_tag(self, elem, name, owner):
        self.prop_id = self.prop_id + 1
        return ",("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"',DEFAULT)"
#        print ",("+`self.prop_id`+","+`elem`+",'"+name+"','"+owner+"',DEFAULT)",
    
    def insert_property_end(self):
        return ";"
    
    # for virtual accelerator pv channel information
    def do_insert(self, itemname, **kw):
        attrs = {}
        params = dict(attrs)
        params.update(kw)
        first = True
    
        cid = self.insert_element(itemname, self.vowner)
        prop_cmd = ''
        for k, v in params.items():
            if first:
                prop_cmd += self.insert_property_begin(cid,k,self.vowner,v)
                first = False
            else:
                prop_cmd += self.insert_property(cid,k,self.vowner,v)
                ## insert_property(cid,k,vowner,v)
                ## insert_property(cid,k,vowner,v)
                ## insert_property(cid,k,vowner,v)
                ## insert_property(cid,k,vowner,v)
                ## insert_property(cid,k,vowner,v)
                ## insert_property(cid,k,vowner,v)
        prop_cmd += self.insert_property_end()
#        print prop_cmd
        self.cursor.execute(prop_cmd)
    
    def get_facility_from_pv(self, pvname):
        if pvname.startswith('SR'):
            return 'storage ring'
        elif pvname.startswith('LI'):
            return 'linac'
        elif pvname.startswith('BS'):
            return 'booster'
    
        return 'unknow'
    
    def get_sub_sys_from_pv(self, pvname):
        pvfields = pvname.split(':')
        cell = pvfields[1][:3]
        gird = pvfields[2][:3]
        return cell, gird
    
    # analysis a pv string reading from pv list file
    # here we assume a pv name has following name convention:
    # SR:C01-BI:G02A<BPM:0>Pos:X
    def insert_items(self, attrs):
        modelIndex = attrs[0]
        pvRB = attrs[1]
        pvSP = attrs[2]
        phyName = attrs[3]
        length = attrs[4]
        position = attrs[5]
        group = attrs[6]
    
        if pvSP != 'NULL':
    #        facility = get_facility_from_pv(pvRB)
            cell, girder = self.get_sub_sys_from_pv(pvRB)
            self.do_insert(phyName, \
                      index = modelIndex, \
                      setpoint = pvSP, \
                      readback = pvRB, \
                      cell = cell, \
                      girder = girder, \
                      length = length, \
                      position = position,\
                      group = group)
        else:
    #        facility = get_facility_from_pv(pvSP)
            cell, girder = self.get_sub_sys_from_pv(pvRB)
            if group == 'BPM' or group == 'TUNE':
                hori = pvRB[:-1] + 'X'
                vert = pvRB[:-1] + 'Y'
    
                self.do_insert(phyName, \
                          index = modelIndex, \
                          horizontal = hori, \
                          vertical = vert, \
                          cell = cell, \
                          girder = girder, \
                          length = length, \
                          position = position,\
                          group = group )
    
       
    def execute(self):
        """The main procedure.
    
        parse the command-line options and perform the command
        """
        try:
            pv_file = open(self.config, 'r')
            lines = pv_file.readlines()
            for line in lines:
                line = line.strip()
                # Make sure line is not empty or commented out
                if line.startswith('!') or line.startswith('#') or len(line) == 0:
                    pass
                else:
                    attrs = line.split()
                    if attrs[3] != self.prev_elem:
                        self.insert_items(attrs)
                    else:
                        pass
                    self.prev_elem = attrs[3]
        except IOError:
            print "I/O error({0}): {1}".format(os.errno, os.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        finally:
            pv_file.close()
        
        self.db.commit()

if __name__ == "__main__":
    config = '../nsls2/va/lat_conf_table.txt'
    if len(sys.argv) > 3:
        host = sys.argv[1]
        user = sys.argv[2]
        pw = sys.argv[3]
        if len(sys.argv) > 4:
            config = sys.argv[4]
    else:
        print 'usage: python build_if_db.py rdb_host rdb_user rdb_pw [lat_conf_table.txt]'
        
    ifdb = build_if_db(config, host=host, user=user, pw=pw)
    ifdb.connect_if_db()
    ifdb.clean_tables()
    ifdb.execute()
