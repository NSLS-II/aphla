import unittest
import aphla as ap

class TestTunes(unittest.TestCase):
    def setUp(self):
        pass

    def test_tunes(self):
        ap.initNSLS2VSR()
        nu = ap.getTunes()
        self.assertEqual(len(nu), 2)
        self.assertGreater(nu[0], 0.0)
        self.assertGreater(nu[1], 0.0)

