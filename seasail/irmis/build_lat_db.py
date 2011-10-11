#!/usr/bin/env python
"""
This class is to read a lattice deck, and load all information into IRMIS database.
It creates 2 temporary tables, telement_rel and telement.
The table depends on the lattice format, and current supported format is as below:
! ElementName  ElementType      L        s        K1         K2       Angle  
!                               m        m       1/m2       1/m3       rad   
!----------------------------------------------------------------------------
 _BEG_        MARK          0        0        0         0          0        
 DH02G1A      DRIF          4.29379  4.29379   0         0          0
 ...

The element name follows the naming convention.

Each time, when loading a new lattice deck, it deletes existing tables, and create new. 
This has to be improved later to support multiple version decks.

@author:    GS, Aug 20, 2010
@copyright: National Synchrotron Light Source II
            Brookhaven National Laboratory, Upton, NY, 11973
@license:   TBD
"""
import sys
import os

import irmis_connect as ic
sys.path.append('../utils/')
import odict


__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

__author__ = 'Guobao Shen (shengb@bnl.gov)'


#GSG1* uniquely defines the start of a cell.  30 count
#GEG6* uniquely defines the end of a girder.  30 count
#GSG* uniquely defines the start of a girder.  180 count
#GEG* uniquely defines the end of a girder.  180 count

class build_lat_db:
    """
    This script assumes what the database named 'tlattice' exist already.
    """
    def __init__(self, lattice, db, cursor):
        self.deck = lattice
        self.element_table = 'telement'
        self.element_rel = 'telement_rel'
        self.z0 = 0.0 #to zero fill telement, telement_rel attributes
        self.index = 0
        self.pre_gird = ''
        self.db = db
        self.cursor = cursor
    
    def connect_close(self):
        self.db.close()
    
    def clean_tables(self):
        # start with new tables;
        self.cursor.execute("delete from %s" %self.element_rel)
        self.cursor.execute("delete from %s" %self.element_table)

        # self.cursor.execute('DROP TABLE IF EXISTS %s.telement_rel' %self.dbname)
        
    def lat_glob(self):
        #    put in the global 'lattice' element
        self.cursor.execute("insert into %s (%s_name, %s_type,insert_date) values ('%s','lattice',now())" \
                       %(self.element_table, self.element_table, self.element_table, self.deck))
        self.db.commit()
        self.cursor.execute("select last_insert_id() as id")
        self.lattice_id = self.cursor.fetchone()[0]
#        print "lattice_id = %s" %self.lattice_id
    
    def get_index(self):
        self.index += 1
        return self.index
    
    # this method should be revised to get correct cell name
    # potential bug here
    def get_cell(self, line):
        attrs = line.split()
        ename = attrs[0]
        # the magic number -4 & -1 should be changed
        return ename[-4:-1]
    
    # this method should be revised to get correct girder name
    # potential bug here
    def get_girder(self, name):
        # the magic number 2 & 4 should be changed
        return name[2:4]
    
    def write_nsls2(self):
        isBegin = True
        first_seq = odict.odict({})
        normal_seq = odict.odict({})
        cell = ''
        
        try:
            lattice_file = open(self.deck, 'r')
            
            for line in lattice_file.readlines():
                # we assume the sequence should start with GS -- Girder Start
                # and end with GE -- Girder End
                line = line.strip()
                # Make sure line is not empty or commented out
                if line.startswith('!') or line.startswith('#') or len(line) == 0:
                    pass
                else:
                    elem_index = self.get_index()
                    if line.startswith('GS'):
                        cellname = self.get_cell(line)
                        if cell != cellname:
                            if cell != '':
                                if isBegin:
                                    isBegin = False
                                else:
                                    # DO database insertion
                                    self.insert_cell(cell, normal_seq)
                                normal_seq.clear()
                            cell = cellname
                    if isBegin:
                        first_seq[elem_index] = line
                    else:
                        normal_seq[elem_index] = line
            if not normal_seq.isempty() or not first_seq.isempty():
                end = normal_seq.byindex(len(normal_seq)-1)[1].split()
                circumference =float(end[3])
                
                # combine 2 pieces into one whole sequence
                for k, v in first_seq.items():
                    normal_seq[k] = v
                self.insert_cell(cell, normal_seq, circumference)
    
        except IOError:
            print "I/O error({0}): {1}".format(os.errno, os.strerror)
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
        finally:
            lattice_file.close()

    def insert_girder(self, parent_id, parent_name, seq, circumference = 0.0):
        start = self.pre_gird.split()
        end = seq.byindex(len(seq)-1)[1].split()
        if  float(end[3]) < float(start[3]):
            length = float(end[3]) - float(start[3]) + circumference
        else:
            length = float(end[3]) - float(start[3])
        pos = float(end[3])
        elem_type = 'GIRDER'
        elem = self.get_girder(end[0]) + parent_name
        self.cursor.execute("""insert into %s (%s_name,%s_type,insert_date,length,s) values ('%s','%s',now(),%s,%s)""" \
                            %(self.element_table, self.element_table, self.element_table, \
                              elem,elem_type, length, pos) )
        self.cursor.execute("select last_insert_id()" )
        girder_id = self.cursor.fetchone()[0]
        self.cursor.execute("""insert into %s (parent_element_id, child_element_id, child_offset_ideal,\
                x_align, y_align, z_align, angle1_align, angle2_align, angle3_align) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) """ \
                %(self.element_rel, parent_id, girder_id, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0)) 
        self.db.commit()
        for k, v in seq.items():
            attrs = v.split()
            self.cursor.execute("""insert into %s (%s_name,%s_type,insert_date,length,s,k1,k2,angle,indx) values ('%s','%s',now(),%s,%s,%s,%s,%s,%s) """ \
                                %(self.element_table, self.element_table, self.element_table, \
                                  attrs[0], attrs[1], float(attrs[2]), float(attrs[3]), float(attrs[4]), float(attrs[5]), float(attrs[6]), k))
            self.cursor.execute("select last_insert_id()" )
            element_id = self.cursor.fetchone()[0]
            self.cursor.execute(""" insert into %s (parent_element_id, child_element_id, child_offset_ideal,\
                                x_align, y_align, z_align, angle1_align, angle2_align, angle3_align) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) """ \
                                %(self.element_rel, girder_id, element_id, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0))
        self.db.commit()
    
    def insert_cell(self, cell, seq, circumference = 0.0):
        cell_start = seq.byindex(0)[1].split()
        cell_end = seq.byindex(len(seq)-1)[1].split()
#        cell_len = 0.0
        
        if float(cell_end[3]) < float(cell_start[3]):
            cell_len = circumference + float(cell_end[3]) - float(cell_start[3])
        else:
            cell_len = float(cell_end[3]) - float(cell_start[3])
        cell_pos = float(cell_end[3])
        elem_type = 'CELL'

        self.cursor.execute("""insert into %s (%s_name,%s_type,insert_date,length,s) values ('%s','%s',now(),%s,%s) """ \
                            %(self.element_table, self.element_table, self.element_table, \
                              cell, elem_type, cell_len, cell_pos))
        self.db.commit()
        self.cursor.execute("select last_insert_id()" )
        cell_id = self.cursor.fetchone()[0]
        self.cursor.execute(""" insert into telement_rel (parent_element_id, child_element_id, child_offset_ideal, \
                        x_align, y_align, z_align, angle1_align, angle2_align, angle3_align) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)""", \
                        (self.lattice_id, cell_id, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0, self.z0) )
        self.db.commit()

        girder_seq = odict.odict({})
        for k, v in seq.items():
            if self.pre_gird == '':
                self.pre_gird = v
            girder_seq[k] = v
            if v.startswith('GE'):
                self.insert_girder(cell_id, cell, girder_seq, circumference)
                
                girder_seq.clear()
                self.pre_gird = v

if __name__ == '__main__':
    lattice = './CD3-Apr07-10-30cell-par.txt'
    host = ''
    user = ''
    pw = ''
    if len(sys.argv) > 3:
        host = sys.argv[1]
        user = sys.argv[2]
        pw = sys.argv[3]
        if len(sys.argv) > 4:
            config = sys.argv[4]
    else:
        print 'usage: python build_lat_db.py rdb_host rdb_user rdb_pw [lat_conf_table.txt]'
        exit()
    
    irmis = ic.irmis_connect('tlattice', host=host, user=user, pw=pw)
    irmis.connect()
    lat = build_lat_db(lattice, irmis.db, irmis.cursor)
    lat.clean_tables()
    lat.lat_glob()
    lat.write_nsls2()
    irmis.close()
