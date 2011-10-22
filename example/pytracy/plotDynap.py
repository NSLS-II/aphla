import matplotlib.pyplot as plt
import pytracy
import numpy

pytracy.Read_Lattice('../CD3-June20-tracy')
# pytracy.Ring_GetTwiss(True,0)

x = 7*[None]
y = 7*[None]
for i in range(7):
    phi = i*numpy.pi/6.
    r = pytracy.getdynap(0.05,phi,0,0.001,50,False)
    x[i] = r*numpy.cos(phi)
    y[i] = r*numpy.sin(phi)

plt.plot(x, y)
plt.axis([-0.05,0.05,0.0,0.02])
plt.title('Dynamic Aperture')
#plt.text(1, 21, r'$\beta_x$')
#plt.text(1, 7, r'$\beta_y$')

plt.show()


