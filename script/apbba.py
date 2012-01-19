#!/usr/bin/env python

import cothread
app = cothread.iqt(use_timer=True)

from cothread.catools import caget, caput
#from aphlas.epicsdatamonitor import CaDataMonitor


import sys
import gui_resources
#import bpmtabledlg
from elementpickdlg import ElementPickDlg
from apbbaconfdlg import BbaConfig
#from orbitplot import OrbitPlot

from PyQt4.QtCore import QSize, SIGNAL, Qt
from PyQt4.QtGui import (QMainWindow, QAction, QActionGroup, QVBoxLayout, 
    QWidget, QTabWidget, QLabel, QIcon, QApplication)

config_dir = "~/.hla"

class BbaMainWindow(QMainWindow):
    """
    the main window
    """
    def __init__(self, parent = None):
        QMainWindow.__init__(self, parent)

        self.setIconSize(QSize(48, 48))
        self.config = BbaConfig(config_dir, "nsls2_sr_bba.json")

        wid = QTabWidget()
        wid.addTab(QLabel("Tab1"), "Tab 1")

        #wid2 = QTableWidget()
        #wid.addTab(wid2, "test2")
        wid.addTab(QLabel("Tab2"), "Tab 2")
        self.setCentralWidget(wid)

        #
        # file menu
        #
        self.fileMenu = self.menuBar().addMenu("&File")
        fileQuitAction = QAction(QIcon(":/file_quit.png"), "&Quit", self)
        fileQuitAction.setShortcut("Ctrl+Q")
        fileQuitAction.setToolTip("Quit the application")
        fileQuitAction.setStatusTip("Quit the application")
        self.connect(fileQuitAction, SIGNAL("triggered()"),
                     self.close)
        fileConfigAction = QAction("&Config", self)
        #
        self.fileMenu.addAction(fileQuitAction)
        self.fileMenu.addAction(fileConfigAction)


        self.controlMenu = self.menuBar().addMenu("&Control")
        controlGoAction =  QAction(QIcon(":/control_play.png"), "&Go", self)
        controlGoAction.setShortcut("Ctrl+G")
        #fileQuitAction.setToolTip("Quit the application")
        #fileQuitAction.setStatusTip("Quit the application")
        #fileQuitAction.setIcon(Qt.QIcon(":/filequit.png"))
        self.controlMenu.addAction(controlGoAction)

        # help
        self.helpMenu = self.menuBar().addMenu("&Help")

        #toolbar = QToolBar(self)
        #self.addToolBar(toolbar)
        fileToolBar = self.addToolBar("File")
        fileToolBar.setObjectName("FileToolBar")
        fileToolBar.addAction(fileQuitAction)
        fileToolBar.addAction(controlGoAction)
        #

    def chooseBpm(self):
        #print self.bpm
        bpm = []
        bpmmask = self.plot1.curve1.mask[:]
        for i in range(len(self.bpm)):
            if bpmmask[i]:
                bpm.append((self.bpm[i], Qt.Unchecked))
            else:
                bpm.append((self.bpm[i], Qt.Checked))

        form = ElementPickDlg(bpm, 'BPM', self)

        if form.exec_(): 
            choice = form.result()
            for i in range(len(self.bpm)):
                if self.bpm[i] in choice:
                    self.plot1.setMask(i, 0)
                    self.plot2.setMask(i, 0)
                else:
                    self.plot1.setMask(i, 1)
                    self.plot2.setMask(i, 1)
        
def main(args = None):
    #app = QApplication(args)
    demo = BbaMainWindow()
    demo.resize(600,500)
    demo.show()

    #sys.exit(app.exec_())
    cothread.WaitForQuit()


# Admire!
if __name__ == '__main__':
    #hla.clean_init()
    main(sys.argv)

# Local Variables: ***
# mode: python ***
# End: ***
