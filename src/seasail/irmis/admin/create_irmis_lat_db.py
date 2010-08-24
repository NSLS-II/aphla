#!/usr/bin/env python
"""
This is script to generate a sql command to create an experimental irmis lattice database.
Two 2 tables are created according the user specified name. 
Only the RDB administrator is allowed to use this script, and do not use it unless 
really necessary.

Created on Aug 23, 2010

@author: GS
@copyright: National Synchrotron Light Source II
            Brookhaven National Laboratory, Upton, NY, 11973
@license:   TBD
"""

class irmis_lattice_db_sql:
    def __init__(self, dbname = 'tlattice', element_table = 'telement', element_rel_table = 'telement_rel'):
        self.dbname = dbname
        self.element_table = element_table
        self.element_rel_table = element_rel_table
        self.FKcount = -1
    
    def get_fk_count(self, bit=2):
        self.FKcount += 1
        return `self.FKcount`.zfill(bit)
    
    def create_irmis_lat_db(self):
        print "CREATE DATABASE IF NOT EXISTS %s;" %self.dbname
        print "DROP TABLE IF EXISTS %s.%s;" %(self.dbname, self.element_rel_table)
        print "DROP TABLE IF EXISTS %s.%s;" %(self.dbname, self.element_table)
    
        print 'SET FOREIGN_KEY_CHECKS=0;'
        
        print "CREATE TABLE  `%s`.`%s` ("  %(self.dbname, self.element_table)
        print "  `%s_id` int(11) NOT NULL AUTO_INCREMENT," %self.element_table
        print "  `%s_name` varchar(50) NOT NULL," %self.element_table
        print "  `%s_type` varchar(10) NOT NULL," %self.element_table
        print "  `insert_date` timestamp DEFAULT CURRENT_TIMESTAMP,"
        print "  `length` double(15, 6),"
        print "  `s` double(15, 6),"
        print "  `k1` double(15, 6),"
        print "  `k2` double(15, 6),"
        print "  `angle` double(15, 6),"
        print "  PRIMARY KEY  (`%s_id`)" %self.element_table
        print ") ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"
    
        print "CREATE TABLE  `%s`.`%s` (" %(self.dbname, self.element_rel_table)
        print "  `%s_id` int(11) NOT NULL AUTO_INCREMENT," %self.element_rel_table
        print "  `parent_element_id` int(11) NOT NULL DEFAULT '0',"
        print "  `child_element_id` int(11) NOT NULL DEFAULT '0',"
        print "   `child_offset_ideal` double(15, 6),"
        print "   `x_align` double(15, 6),"
        print "   `y_align` double(15, 6),"
        print "   `z_align` double(15, 6),"
        print "   `angle1_align` double(15, 6),"
        print "   `angle2_align` double(15, 6),"
        print "   `angle3_align` double(15, 6),"
        print "  PRIMARY KEY  (`%s_id`)," %self.element_rel_table
        print "  CONSTRAINT `Ref_%s` FOREIGN KEY (`parent_element_id`) REFERENCES `%s` (`%s_id`) ON DELETE NO ACTION ON UPDATE NO ACTION," %(self.get_fk_count(2), self.element_table, self.element_table)
        print "  CONSTRAINT `Ref_%s` FOREIGN KEY (`child_element_id`) REFERENCES `%s` (`%s_id`) ON DELETE NO ACTION ON UPDATE NO ACTION" %(self.get_fk_count(2), self.element_table, self.element_table)
        print ") ENGINE=INNODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"

        print 'SET FOREIGN_KEY_CHECKS=1;'

if __name__ == '__main__':
    
    db = irmis_lattice_db_sql()
    db.create_irmis_lat_db()