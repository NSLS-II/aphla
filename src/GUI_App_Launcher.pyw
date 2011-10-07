#! /usr/bin/env python

"""

GUI application for launching other GUI applications

:author: Yoshiteru Hidaka
:license:

This GUI application is a launcher program that allows users to start any
individual application they want to use with a single click on a button in
the GUI panel.

"""

import sys

import cothread

import PyQt4.Qt as Qt

import hla
from Qt4Designer_files.ui_launcher import Ui_MainWindow


########################################################################
class LauncherApp(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        self._initData()
        self._initView()
        
    #----------------------------------------------------------------------
    def _initData(self):
        """"""
        
        self.data = LauncherData()
        
    #----------------------------------------------------------------------
    def _initView(self):
        """"""
        
        self.view = LauncherView(self.data)
        
########################################################################
class LauncherData(Qt.QObject):
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        
        Qt.QObject.__init__(self)
        
        
########################################################################
class LauncherView(Qt.QMainWindow, Ui_MainWindow):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, data):
        """Constructor"""
        
        Qt.QMainWindow.__init__(self)
        
        self.data = data
    
        # Set up the user interface from Designer
        self.setupUi(self)
        
        self.statusBar().showMessage("test")
    
        self.connect(self.pushButton_01,Qt.SIGNAL('clicked()'),
                     self.startCurrentMonitor_1)
        
        self.connect(self.pushButton_02,Qt.SIGNAL('clicked()'),
                     self.startCurrentMonitor_2)
        
    #----------------------------------------------------------------------
    def startCurrentMonitor_1(self):
        """"""
                
        # You need to make sure that the object returned from the
        # "make()" function will not get erased at the end of this
        # function call. The object is a GUI object. If it is
        # cleared, the GUI window will also disappear. In order
        # to keep the object in the memory, either store it in
        # "self", or declare the returned object as "global".
        # Then the opened GUI window will not disappear immediately.
        self.app_CurrentMonitor_1 = \
            __import__('GUI_Current_Monitor').make()

     #----------------------------------------------------------------------
    def startCurrentMonitor_2(self):
        """"""


        # You need to make sure that the object returned from the
        # "make()" function will not get erased at the end of this
        # function call. The object is a GUI object. If it is
        # cleared, the GUI window will also disappear. In order
        # to keep the object in the memory, either store it in
        # "self", or declare the returned object as "global".
        # Then the opened GUI window will not disappear immediately.
        self.app_CurrentMonitor_2 = \
            __import__('GUI_Current_Monitor').make()   
        
        
#----------------------------------------------------------------------
def main(args):
    """"""
    
    
    # If Qt is to be used (for any GUI) then the cothread library needs to be informed,
    # before any work is done with Qt. Without this line below, the GUI window will not
    # show up and freeze the program.
    qtapp = cothread.iqt()
    
    app = LauncherApp()
    window = app.view
    window.show()
    
    cothread.WaitForQuit()
    
    
    
    
#----------------------------------------------------------------------    
if __name__ == "__main__":
    
    main(sys.argv)
    