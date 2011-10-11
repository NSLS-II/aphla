import numpy as np
from cothread.catools import camonitor, caget

class CaDataMonitor:
    def __init__(self, pvs, samples=20):
        self.samples = samples

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
        self.recent = np.zeros(n, 'd')

        for i in range(self.samples):
            self.data[:,i] = caget(self.pvs)

        self.recent[:] = self.data[:,-1]
        self.avg[:]    = np.average(self.data, axis=1)
        self.std[:]    = np.std(self.data, axis=1)
        #print type(self.recent)

        self.monitors = camonitor(self.pvs, self._ca_update)
        
    def closeMonitors(self):
        for p in self.monitors:
            p.close()
        self.monitors = []

    def _ca_update(self, val, idx):
        #print "updating", val, idx, self.avg[idx], self.std[idx]
        self.recent[idx] = val
        i0 = self._icur[idx]
        self.data[idx, i0] = val
        self.avg[idx] = self.avg[idx] + (val - self.data[idx, i0-1])/self.samples
        self._icur[idx] = (i0 + 1) % self.samples
        self.std[idx] = np.std(self.data[idx,:])

    def __delete__(self, instance):
        if instance == "monitors":
            self.closeMonitors()

    #def __del__(self):
    #    self.closeMonitors()
    #    print "Closing"
    #    cothread.WaitForClose()

if __name__ == "__main__":
    import time
    a = CaDataMonitor(['SR:C01-BI:G02A{BPM:L1}SA:X-I', 'SR:C01-BI:G02A{BPM:L1}SA:Y-I'])
    print a.data

    print "A"

    import cothread
    cothread.WaitForQuit()
