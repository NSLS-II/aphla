import unittest
import aphla as ap
import numpy as np
import time

class TestTunes(unittest.TestCase):
    def setUp(self):
        ap.initNSLS2VSR()
        ap.initNSLS2VSRTwiss()
        pass

    def test_tunes(self):
        nu = ap.getTunes()
        self.assertEqual(len(nu), 2)
        self.assertGreater(nu[0], 0.0)
        self.assertGreater(nu[1], 0.0)

    @unittest.skip
    def test_dispersion_meas(self):
        #s, etax, etay = ap.measDispersion('*')
        eta = ap.measDispersion('P*C0[2-4]*')
        s, etax, etay = eta[:,-1], eta[:,0], eta[:,1]

        if False:
            import matplotlib.pylab as plt
            plt.clf()
            plt.plot(s, etax, '-x', label=r'$\eta_x$')
            plt.plot(s, etay, '-o', label=r'$\eta_y$')
            plt.legend(loc='upper right')
            plt.savefig('test_twiss_dispersion_meas.png')

        self.assertGreater(max(abs(etax)), 0.15)
        self.assertGreater(max(abs(etay)), 0.0)
        self.assertGreater(min(abs(s)), 0.0)

    def test_phase_get(self):
        phi = ap.machines.getLattice().getPhase('P*C1[0-1]*')
        s, phix, phiy = phi[:,-1], phi[:,0], phi[:,1]
        if False:
            import matplotlib.pylab as plt
            plt.clf()
            plt.plot(s, phix, '-x', label=r'$\phi_x$')
            plt.plot(s, phiy, '-o', label=r'$\phi_y$')
            plt.legend(loc='upper left')
            plt.savefig('test_twiss_phase_get.png')            
        pass


    def test_beta_get(self):
        beta = ap.machines.getLattice().getBeta('P*C1[5-6]*')
        s, twx, twy = beta[:,-1], beta[:,0], beta[:,1]
        if False:
            import matplotlib.pylab as plt
            twl = ap.machines.getLattice().getBeamlineProfile(s[0], s[-1])
            sprof, vprof = [], []
            for tw in twl:
                sprof.extend(tw[0])
                vprof.extend(tw[1])

            plt.clf()
            plt.plot(sprof, vprof, 'k-')
            plt.plot(s, twx, '-x', label=r'$\beta_x$')
            plt.plot(s, twy, '-o', label=r'$\beta_y$')
            plt.legend(loc='upper right')
            plt.savefig('test_twiss_beta_get.png')            
        self.assertGreater(max(abs(twx)), 20.0)
        self.assertGreater(max(abs(twy)), 20.0)

        pass

    def test_tune_get(self):
        """
        The tunes stored in lattice._twiss is not live, while ap.getTunes is
        live.
        """

        lat = ap.machines.getLattice()
        tunes0a = lat.getTunes()
        self.assertAlmostEqual(tunes0a[0], 33.41, places=2)
        self.assertAlmostEqual(tunes0a[1], 16.31, places=2)

        # adjust quad, live tune should change
        qs = lat.getElementList('QUAD')
        k1 = qs[0].k1
        qs[0].k1 = k1 * 1.02
        time.sleep(3)
        try:
            tunes0b = lat.getTunes()
            tunes1 = ap.getTunes()
        finally:
            qs[0].k1 = k1
        
        self.assertEqual(tunes0a[0], tunes0b[0])
        self.assertEqual(tunes0a[1], tunes0b[1])
        self.assertNotEqual(tunes0b[0], tunes1[0])
        self.assertNotEqual(tunes0b[1], tunes1[1])
        

    def test_chromaticities(self):
        lat = ap.machines.getLattice()
        ch = lat.getChromaticities()
        self.assertEqual(abs(ch[0]), 0)
        self.assertEqual(abs(ch[1]), 0)
        pass
