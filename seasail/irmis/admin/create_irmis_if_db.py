#!/usr/bin/env python
"""
This is script to generate a sql command to create an experimental irmis database
for itemfinder service. Two 2 tables are created according the user specified name.
Only the RDB administrator is allowed to use this script, and do not use it unless 
really necessary.

Created on Aug 23, 2010

@author: GS
@copyright: National Synchrotron Light Source II
            Brookhaven National Laboratory, Upton, NY, 11973
@license:   TBD
"""

class irmis_lattice_if_sql:
    def __init__(self, dbname = 'itemfinder', element_table = 'element', property_table = 'property'):
        self.dbname = dbname
        self.element_table = element_table
        self.property_table = property_table
        self.FKcount = -1
    
    def get_fk_count(self, bit=2):
        self.FKcount += 1
        return `self.FKcount`.zfill(bit)
    
    def create_irmis_if_db(self):
        print "CREATE DATABASE IF NOT EXISTS %s;" %self.dbname
        print "DROP TABLE IF EXISTS %s.%s;" %(self.dbname, self.property_table)
        print "DROP TABLE IF EXISTS %s.%s;" %(self.dbname, self.element_table)
    
        print "CREATE TABLE  `%s`.`%s` (" %(self.dbname, self.element_table)
        print "  `id` int(10) unsigned NOT NULL auto_increment,"
        print "  `name` varchar(45) NOT NULL,"
        print "  `owner` varchar(45) NOT NULL,"
        print "  PRIMARY KEY  (`id`)"
        print ") ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"
    
        print "CREATE TABLE  `%s`.`%s` ("  %(self.dbname, self.property_table)
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

if __name__ == '__main__':
    
    db = irmis_lattice_if_sql()
    db.create_irmis_if_db()