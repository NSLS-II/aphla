import matplotlib.pyplot as plt
import pytracy

pytracy.Read_Lattice('../CD3-June20-tracy')
pytracy.Ring_GetTwiss(True,0)

s=pytracy.getS()
bx=pytracy.getBetaX()
by=pytracy.getBetaY()


plt.plot(s,bx,s,by,'r')
plt.axis([0,s[-1]/15,0,35])
plt.title('Beta functions')
plt.text(1, 21, r'$\beta_x$')
plt.text(1, 7, r'$\beta_y$')

plt.show()


