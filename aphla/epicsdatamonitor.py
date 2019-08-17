from __future__ import print_function, division, absolute_import

"""
EPICS Data Monitor
-------------------

"""

# :author: Lingyun Yang <lyyang@bnl.gov>

import numpy as np
from cothread.catools import camonitor, caget
import threading, time
import random

class SimData(threading.Thread):
    def __init__(self, update, nmax):
        #super(threading.Thread, self).__init__()
        self.update = update
        self.N = nmax
        self.exitFlag = 0
        threading.Thread.__init__(self)

    def run(self):
        print("Running simdata")
        while not self.exitFlag:
            time.sleep(1)
            i = random.randint(0, self.N-1)
            val = random.random()
            self.update(val, i)
            print('{0}, {1}'.format(i, val))

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

        n = 1
        if isinstance(pvs, (list, tuple)):
            n = len(pvs)
            self.pvs = pvs[:]
        elif isinstance(pvs, str):
            n = 1
            self.pvs = [pvs]

        self.data = np.zeros((n, self.samples), 'd')
        self.std = np.zeros(n, 'd')
        self.avg = np.zeros(n, 'd')
        self._icur = np.zeros(n, 'i')
        self._count = np.ones(n, 'i')
        self.recent = np.zeros(n, 'd')


        if not self.simulation:
            for i in range(self.samples):
                self.data[:,i] = caget(self.pvs)

            self.recent[:] = self.data[:,-1]
            self.avg[:]    = self.recent[:] #np.average(self.data, axis=1)
            #self.std[:]    = #np.std(self.data, axis=1)
            #print type(self.recent)
            self.monitors = camonitor(self.pvs, self._ca_update)
        else:
            self.monitors = SimData(self._ca_update, len(self.pvs))
            self.monitors.start()
            print("Thread is running")

    def closeMonitors(self):
        if self.simulation:
            self.monitors.exitFlag = 1
            time.sleep(2)
        else:
            for p in self.monitors:
                p.close()
            self.monitors = []

    def resetData(self):
        """
        set PV data to zero
        """
        self.data.fill(0.0)
        self.std.fill(0.0)
        self.avg.fill(0.0)
        self._icur.fill(0)
        self.recent.fill(0.0)

    def _ca_update(self, val, idx):
        """
        update the reading, average, index and variance.
        """
        print("updating {0}, {1}, {2}, {3}".format(
            val, idx, self.avg[idx], self.std[idx]))
        self.recent[idx] = val
        self._count[idx] += 1
        i0 = self._icur[idx]
        self.data[idx, i0] = val
        self.avg[idx] = self.avg[idx] + (val - self.data[idx, i0-1])/self.samples
        self._icur[idx] = (i0 + 1) % self.samples
        if self._count[idx] >= self.samples:
            self.std[idx] = np.std(self.data[idx,:])
        else:
            self.std[idx] = np.std(self.data[idx, :i0+2])

    def __delete__(self, instance):
        if instance == "monitors":
            self.closeMonitors()

    #def __del__(self):
    #    self.closeMonitors()
    #    print "Closing"
    #    cothread.WaitForClose()

def _test1():
    import time
    a = CaDataMonitor(['V:2-SR:C02-BI:G2{PH1:245}SA:X', 'V:2-SR:C02-BI:G2{PH1:245}SA:Y'])
    print(a.data)

    print("A")

    a.closeMonitors()

    print("press Ctrl-C to quit")
    import cothread
    cothread.WaitForQuit()

def _test2():
    import time
    a = CaDataMonitor(['a', 'b', 'c'], simulation=True)
    print("created, sleeping")
    time.sleep(5)
    print("Sleep done")
    a.closeMonitors()

    b = CaDataMonitor(['a', 'b', 'c'], simulation=True)
    print("created, sleeping")
    time.sleep(5)
    print("Sleep done")
    b.closeMonitors()

if __name__ == "__main__":
    _test1()
