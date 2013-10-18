from cothread.catools import caget, caput
import time
import matplotlib.pylab as plt
import numpy as np

freq0 = 499.654031
caput('V:1-SR-RF:SUPER{RF:1540}Freq:SP', freq0)
caput('V:1-SR-RF:SUPER{RF:1540}Freq:SP', freq0)
time.sleep(3.0)
orbit0 = caget('V:1-SR-BI{ORBIT}X-I')
caput('V:1-SR-RF:SUPER{RF:1540}Freq:SP', freq0 + 0.003)
caput('V:1-SR-RF:SUPER{RF:1540}Freq:SP', freq0 + 0.003)
time.sleep(3.0)
orbit1 = caget('V:1-SR-BI{ORBIT}X-I')

plt.clf()
plt.subplot(211)
plt.plot(orbit0, '-')
plt.plot(orbit1, 'o')
d = np.array(orbit1) - np.array(orbit0)
plt.subplot(212)
plt.plot(d, '-x')
plt.savefig("test.png")


