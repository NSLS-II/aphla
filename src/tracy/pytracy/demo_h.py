# import matplotlib.pyplot as plt
import numpy
import pytracy

pytracy.Read_Lattice('../CD3-June20-tracy')
pytracy.Ring_GetTwiss(True,0)



# function [ out ] = geth(  )
# %GETH Summary of this function goes here
# %   Detailed explanation goes here
# global THERING;
# [TD TUNE CHROM]=twissring(THERING, 0, 1:length(THERING),'chrom');

# out = zeros(1, 21);
h11001 = 0
h00111 = 0  
h20001 = 0  
h00201 = 0  
h10002 = 0  

h21000 = 0  
h30000 = 0  
h10110 = 0  
h10020 = 0  
h10200 = 0  

h22000 = 0  
h11110 = 0  
h00220 = 0  
h31000 = 0  
h40000 = 0  

h20110 = 0  
h11200 = 0  
h20020 = 0  
h20200 = 0  
h00310 = 0  
h00400 = 0  


# NE = length(THERING);
sextList = pytracy.getSextList()
quadList = pytracy.getQuadList()
magList = quadList + sextList
magList.sort()
phix = pytracy.getPhiX()
phiy = pytracy.getPhiY()
etax = pytracy.getEtaX()
betax = pytracy.getBetaX()
betay = pytracy.getBetaY()

for k in magList:
    info = pytracy.getCellInfo(k)
    b2L = 0
    b3L = 0
    if k in quadList:
	try:
            b2L = info['Length']*info['Bn'][1]
	except:
	    continue
    else:
	try:
            b3L = info['Length']*info['Bn'][2]
	except:
	    continue

    phx = (phix[k-1]+phix[k])/2
    phy = (phiy[k-1]+phiy[k])/2
    
    ex = (etax[k-1]+etax[k])/2
    bx = (betax[k-1] + betax[k])/2
    by = (betay[k-1] + betay[k])/2
    coef = b2L-2*b3L*ex
    h11001 = h11001 + coef*bx/4
    h00111 = h00111 - coef*by/4

    h20001 = h20001 + coef*bx/8*numpy.exp(2j*phx)
    h00201 = h00201 - coef*by/8*numpy.exp(2j*phy)

    coef = b2L-b3L*ex
    h10002 = h10002 + coef/2*ex*numpy.sqrt(bx)*numpy.exp(1j*phx)

    coef = -b3L/8*bx**1.5
    h21000 = h21000 + coef*numpy.exp(phx*1j)

    coef = coef/3
    h30000 = h30000 + coef*numpy.exp(3j*phx)

    coef = b3L/4.0*numpy.sqrt(bx)*by
    h10110 = h10110 + coef*numpy.exp(1j*phx)

    coef = coef/2
    h10020 = h10020 + coef*numpy.exp(phx*1j-2j*phy)
    h10200 = h10200 + coef*numpy.exp(phx*1j+2j*phy)

h12000 = h21000.conjugate()
h22000 = (3*abs(h21000)**2 + abs(h30000)**2)/64.0

t1 = 2*h21000*h10110.conjugate()
t2 = h10020*h10020.conjugate()
t3 = h10200*h10200.conjugate()
h11110 = (t1+t2+t3)/16.0

h00220 = (4*abs(h10110)**2 + abs(h10020)**2 + abs(h10200)**2)/64.0

h31000 = h30000*h21000.conjugate()/32.0

h40000 = h30000*h21000/64.0

t1 = 2*h30000*h10110.conjugate()
t2 = 2*h21000*h10110
t3 = 4*h10200*h10020
h20110 = (t1 + t2 + t3)/64.0

t1 = 2*h10200*h12000
t2 = 2*h21000*h10020.conjugate()
t3 = 4*h10200 * h10110.conjugate()
t4 = 4*h10110*h10020.conjugate()
h11200 = (t1 + t2 + t3 + t4)/64.0

t1 = h21000*h10020
t2 = h30000*h10200.conjugate()
t3 = 4*h10110*h10020
h20020 = (t1 + t2 + t3)/64.0

t1 = h30000*h10020.conjugate()/64.0
t2 = h10200*h21000/64.0
t3 = h10110*h10200/16.0
h20200 = (t1 + t2 + t3)

t1 = h10200*h10110.conjugate()
t2 = h10110*h10020.conjugate()
h00310 = (t1 + t2)/32.0

h00400 = h10200*h10020.conjugate()/64.0

nux = pytracy.globval.TotalTune[0]
nuy = pytracy.globval.TotalTune[1]

dnux_dJx = 0
dnux_dJy = 0
dnuy_dJy = 0



for k in sextList:
    info1 = pytracy.getCellInfo(k)
    try:
        b3L1 = info1['Length']*info['Bn'][2]
    except:
	continue
                
    phx1 = (phix[k-1]+phix[k])/2
    phy1 = (phiy[k-1]+phiy[k])/2
    
#   ex1 = (etax[k-1]+etax[k])/2
    bx1 = (betax[k-1] + betax[k])/2
    by1 = (betay[k-1] + betay[k])/2
             
    for l in sextList:
        info2 = pytracy.getCellInfo(l)
        try:
            b3L2 = info2['Length']*info['Bn'][2]
        except:
	    continue
        phx2 = (phix[l-1]+phix[l])/2
        phy2 = (phiy[l-1]+phiy[l])/2
    
#   ex1 = (etax[k-1]+etax[k])/2
        bx2 = (betax[l-1] + betax[l])/2
        by2 = (betay[l-1] + betay[l])/2

        dnux_dJx = dnux_dJx + b3L1*b3L2/(-16*numpy.pi)*(bx1*bx2)**1.5* \
                            (3*numpy.cos(abs(phx1-phx2)-numpy.pi*nux)/numpy.sin(numpy.pi*nux) + numpy.cos(abs(3*(phx1-phx2))-3*numpy.pi*nux)/numpy.sin(3*numpy.pi*nux))
        dnux_dJy = dnux_dJy + b3L1*b3L2/(8*numpy.pi)*numpy.sqrt(bx1*bx2)*by1*(2*bx2*numpy.cos(abs(phx1-phx2)-numpy.pi*nux)/numpy.sin(numpy.pi*nux)  \
                            - by2*numpy.cos(abs(phx1-phx2)+2*abs(phy1-phy2)-numpy.pi*(nux+2*nuy))/numpy.sin(numpy.pi*(nux+2*nuy))  \
                            + by2*numpy.cos(abs(phx1-phx2)-2*abs(phy1-phy2)-numpy.pi*(nux-2*nuy))/numpy.sin(numpy.pi*(nux-2*nuy)))
        dnuy_dJy = dnuy_dJy + b3L1*b3L2/(-16*numpy.pi)*numpy.sqrt(bx1*bx2)*by1*by2*(4*numpy.cos(abs(phx1-phx2)-numpy.pi*nux)/numpy.sin(numpy.pi*nux)  \
                            + numpy.cos(abs(phx1-phx2)+2*abs(phy1-phy2)-numpy.pi*(nux+2*nuy))/numpy.sin(numpy.pi*(nux+2*nuy))  \
                            + numpy.cos(abs(phx1-phx2)-2*abs(phy1-phy2)-numpy.pi*(nux-2*nuy))/numpy.sin(numpy.pi*(nux-2*nuy)))
#out = [abs(h11001) abs(h00111) abs(h20001) abs(h00201) abs(h10002) abs(h21000) abs(h30000)  \
#       abs(h10110) abs(h10020) abs(h10200) abs(h22000) abs(h11110) abs(h00220) abs(h31000)  \
#       abs(h40000) abs(h20110) abs(h11200) abs(h20020) abs(h20200) abs(h00310) abs(h00400)]

print [h11001,h00111,h20001,h00201,h10002,h21000,h30000, \
       h10110,h10020,h10200,h22000,h11110,h00220,h31000, \
       h40000,h20110,h11200,h20020,h20200,h00310,h00400, \
       dnux_dJx,dnux_dJy,dnuy_dJy]
    
    
    
# s=pytracy.getS()
# bx=pytracy.getBetaX()
# by=pytracy.getBetaY()


# plt.plot(s,bx,s,by,'r')
# plt.axis([0,s[-1]/15,0,35])
# plt.title('Beta functions')
# plt.text(1, 21, r'$\beta_x$')
# plt.text(1, 7, r'$\beta_y$')
# 
# plt.show()


