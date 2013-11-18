"""
EPICS PV Data Monitor
----------------------

"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import numpy as np
import cothread

if __name__ == "__main__":
    app = cothread.iqt()

from cothread.catools import camonitor, caget
import threading, time
import random

from PyQt4 import QtGui

class CaDataMonitor:
    def __init__(self, pvs, samples=20, **kwargs):
        """
        - pvs a list of PV
        - samples number of data points for std/var/average

        optional:
        - simulation [True|False] use simulated data or real pv data
        """
        self.samples = samples
        
        self.simulation = kwargs.get('simulation', False)
        self.val_default = kwargs.get("default", np.nan)
        timeout = kwargs.get("timeout", 2)
        self.pvs = []
        self.data = {}
        self._count = []
        self._buf = {}
        self._icur = []
        self._dead = []
        self.monitors = []

        if not pvs: return

        if isinstance(pvs, (list, tuple)):
            # convert to uniq list
            self.pvs = list(set(pvs))
        elif isinstance(pvs, str):
            self.pvs = [pvs]

        self.resetData(timeout)

        self.monitors = camonitor(self.pvs, self._ca_update,
                                  format=cothread.catools.FORMAT_TIME,
                                  throw = False)

    def closeMonitors(self):
        for p in self.monitors: p.close()
        self.monitors = []

    def resetData(self, timeout):
        """
        set PV data to zero
        """
        # update data
        n = len(self.pvs)
        d0 = caget(self.pvs, timeout=timeout, throw=False)
        self._dead = []
        self._count = [1] * n
        self._icur = [1] * n
        for i,pv in enumerate(self.pvs):
            if d0[i].ok:
                self.data[pv] = d0[0]
                self._buf[pv] = [d0[i]]
                #if pv in self._dead: self._dead.pop(self._dead.index(pv))
            else: 
                self._dead.append(pv)
                self._count[i] = 0
                self._icur[i] = 0
        #print "d0=", d0
        print "dead=", self._dead



    def addPv(self, pv):
        if pv in self.pvs: return
        for m in self.monitors: m.close()
        self.pvs.append(pv)
        self.resetData(2)
        self.monitors = camonitor(self.pvs, self._ca_update,
                                  format=cothread.catools.FORMAT_TIME)

    def addPvList(self, pvlst):
        cpvlst = [pv for pv in pvlst if pv not in self.pvs]
        if not cpvlst: return

        self.pvs = list(set(cpvlst + self.pvs))
        for m in self.monitors: m.close()
        self.resetData(2)

        self.monitors = camonitor(self.pvs, self._ca_update,
                                  format=cothread.catools.FORMAT_TIME)


    def _ca_update(self, val, idx):
        """
        update the reading, average, index and variance.
        """
        self._count[idx] += 1
        pv = self.pvs[idx]
        #print "updating", pv, val, self._count[idx],
        #if self._count[idx] % 5 == 0:
        #    print "updating", self.pvs[idx], val, self._count[idx]
        if self._count[idx] < self.samples:
            self._buf[pv].append(val)
        else:
            self._buf[self._icur[idx]] = val
            self._icur[idx] = (self._icur[idx] + 1) % self.samples
        #if self._count[idx] > 1: print val - self.data[pv]
        #else: print 0.0
        self.data[pv] = val

    def get(self, pv, default = np.nan):
        if pv in self._dead: return None
        return self.data.get(pv, default)

    def dead(self, pv):
        return (pv in self._dead)


class Example(QtGui.QWidget):
    
    def __init__(self, pvs):
        super(Example, self).__init__()
        
        self.cadata = CaDataMonitor(pvs)
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        
        self.setToolTip('This is a <b>QWidget</b> widget')
        self.lbl = []
        fmlayout = QtGui.QFormLayout()
        for pv in pvs:
            self.lbl.append(QtGui.QLabel(""))
            fmlayout.addRow(pv, self.lbl[-1])
        bt1 = QtGui.QPushButton("Click 1", self)
        bt1.clicked.connect(self.show_msg)
        fmlayout.addRow("Test:", bt1)
        self.setLayout(fmlayout)
        #self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Tooltips')    
        self._timerId = self.startTimer(1000)
        #self.show()


    def timerEvent(self, e):
        for i,lbl in enumerate(self.lbl):
            # print "timer ..."
            pv = self.cadata.pvs[i]
            d = self.cadata.data[pv]
            lbl.setText("{0}".format(d))
            #print d.ok, d.timestamp, d.datetime, dir(d)

    def show_msg(self):
        QtGui.QMessageBox.critical(
            self, "aphla", "Testing", QtGui.QMessageBox.Ok)

def _test1(pvs):
    a = CaDataMonitor(pvs)
    cothread.WaitForQuit()


if __name__ == "__main__":
    pvs = ["V:2-SR:C30-BI:G2{PH1:11}SA:X",
           "V:2-SR:C30-BI:G2{PH1:11}SA:Y",
           "V:2-SR:C30-BI:G2{PH2:26}SA:X",
           "V:2-SR:C30-BI:G2{PH2:26}SA:Y",
           "V:2-SR:C30-BI:G4{PM1:55}SA:X",
           "V:2-SR:C30-BI:G4{PM1:55}SA:Y",
           "V:2-SR:C30-BI:G4{PM1:65}SA:X",
           "V:2-SR:C30-BI:G4{PM1:65}SA:Y",
           "V:2-SR:C30-BI:G6{PL1:105}SA:X",
           "V:2-SR:C30-BI:G6{PL1:105}SA:Y"]
    

    #_test1(pvs)
    ex = Example(pvs)
    ex.show()
    cothread.WaitForQuit()

