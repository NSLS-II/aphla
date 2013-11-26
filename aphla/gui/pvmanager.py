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
from collections import deque

from PyQt4 import QtGui

class CaDataMonitor:
    def __init__(self, pvs = [], **kwargs):
        """
        - pvs a list of PV
        - samples number of data points for std/var/average

        optional:
        - simulation [True|False] use simulated data or real pv data
        """
        self.samples     = kwargs.get("samples", 10)
        self.simulation  = kwargs.get('simulation', False)
        self.val_default = kwargs.get("default", np.nan)
        self.timeout     = kwargs.get("timeout", 2)
        self.data = {}
        self._monitors = {}
        self._dead = set()

        if pvs: self.addPv(pvs)

    def addPv(self, pvs):
        """add a pv or list of pvs"""
        if not pvs: return

        kw_cg = {"format": cothread.catools.FORMAT_CTRL,
                 "timeout": self.timeout,
                 "throw": False}
        kw_cm = {"format": cothread.catools.FORMAT_TIME }

        if isinstance(pvs, (list, tuple, set)):
            newpvs = [ pv for pv in pvs if pv not in self.data ]
        elif isinstance(pvs, str) and pvs not in self.data:
            newpvs = [ pvs ]
        else:
            newpvs = []
        
        if len(newpvs) == 0: return

        d = caget(newpvs, **kw_cg)
        newmons = camonitor(newpvs, self._ca_update, **kw_cm)
        for i,pv in enumerate(newpvs):
            if not d[i].ok:
                self._dead.add(newpvs[i])
            else:
                self._monitors[pv] = newmons[i]
                self.data[pv] = deque([d[i]], self.samples)

    def _ca_update(self, val, idx = None):
        """
        update the reading, average, index and variance.
        """
        pv = val.name
        if val.ok and pv in self.data: self.data[pv].append(val)
        #print "updating", idx, val, val.name, len(self.data[pv])

    def close(self, pv):
        p = self._monitors.get(pv, None)
        if p is None: return
        p.close()
        self._monitors[pv] = None
        self.data[pv].clear()

    def get(self, pv, default = np.nan):
        if pv in self._dead: return default
        lst = self.data.get(pv, [])
        if len(lst) == 0: return default
        elif not lst[-1].ok: return default
        return lst[-1]

    def dead(self, pv):
        return (pv in self._dead)

    def __len__(self):
        return len(self.data)

    def activeCount(self):
        return len([True for pv,cam in self._monitors.items()
                    if cam is not None])

    def deadCount(self):
        return len([True for pv,cam in self._monitors.items()
                    if cam is None])


class Example(QtGui.QWidget):
    
    def __init__(self, pvs):
        super(Example, self).__init__()
        
        self.pvs = pvs
        self.cadata = CaDataMonitor()
        self.cadata.addPv(pvs)

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
        self.count = 0

    def timerEvent(self, e):
        if e.timerId() != self._timerId: return

        for i,lbl in enumerate(self.lbl):
            # print "timer ..."
            pv = self.pvs[i]
            d = self.cadata.get(pv, None)
            lbl.setText("{0}".format(d))
            #print d.ok, d.timestamp, d.datetime, dir(d)
        self.count += 1
        #if self.count > 5:
        #    self.cadata.close(self.pvs[self.count - 5])

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

