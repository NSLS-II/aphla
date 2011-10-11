'''
Created on Aug 26, 2010

@author: shen
'''

import MySQLdb

class irmis_connect:
    '''
    classdocs
    '''

    def __init__(self, db, host='localhost', user='test' , pw='test_pw', port=3306):
        '''
        Constructor
        '''
        self.host = host
        self.user = user
        self.pw = pw
        self.dbname = db
        self.port = port

        
    def connect(self):
        try:
            self.db= MySQLdb.connect(host=self.host, user=self.user, passwd=self.pw, db=self.dbname, port=self.port)
            self.cursor= self.db.cursor()
        except:
            print 'wrong user name and password for database: %s' %self.dbname
            raise

    def close(self):
        self.db.close()
    
