import sys

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
elif sys.version_info[:2] == (2,7):
    import unittest

import numpy as np
import aphla as ap

class TestFitting(unittest.TestCase):
    def setUp(self):
        self.sig = 0.7
        self.avg = 1.3
        self.amp = 3.0
        self.x = np.linspace(-3, 3, 300) + self.avg
        self.x1 = np.linspace(self.x[0], self.x[-1], 1000)
        #C = 1.0/(self.sig*np.sqrt(2.0*np.pi))
        C = 1.0
        self.y = self.amp*C*np.exp(-.5*(self.x - self.avg)**2/self.sig**2)
        self.y1 = self.amp*C*np.exp(-.5*(self.x1 - self.avg)**2/self.sig**2)

    def test_fit_gaussian(self):
        try:
            import matplotlib.pylab as plt
            plt.plot(self.x, self.y, 'o')
            plt.plot(self.x1, self.y1, '-')
            plt.savefig("test.png")
        except:
            pass

        C = ap.fitGaussian1(self.x, self.y)
        #print C
        self.assertAlmostEqual(C[0], self.amp, places=3)
        self.assertAlmostEqual(C[1], self.avg, places=3)
        self.assertAlmostEqual(C[2], self.sig, places=3)

    def _gaussian(self, height, center_x, center_y, width_x, width_y):
        """Returns a gaussian function with the given parameters"""
        width_x = float(width_x)
        width_y = float(width_y)
        return lambda x,y: height*np.exp(
            -(((center_x-x)/width_x)**2+((center_y-y)/width_y)**2)/2)

    def test_fit_gaussian_2d(self):
        import matplotlib.pylab as plt
        # Create the gaussian data
        Xin, Yin = plt.mgrid[0:201, 0:201]
        data = self._gaussian(3, 100, 100, 20, 40)(Xin, Yin) + \
            np.random.random(Xin.shape)

        plt.clf()
        ax2 = plt.axes([0, 0.52, 1.0, 0.4])
        ax2.matshow(data, cmap=plt.cm.gist_earth_r)

        params = ap.fitGaussianImage(data)
        fit = self._gaussian(*params)

        ax2.contour(fit(*np.indices(data.shape)), cmap=plt.cm.cool)
        (height, x, y, width_x, width_y) = params

        plt.text(0.95, 0.05, """
        x : %.1f
        y : %.1f
        width_x : %.1f
        width_y : %.1f""" %(x, y, width_x, width_y),
             fontsize=16, horizontalalignment='right',
             verticalalignment='bottom', transform=ax2.transAxes)

        ax1 = plt.axes([0, 0.08, 1.0, 0.4])
        
        #plt.savefig("test.png")

