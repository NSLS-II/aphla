from __future__ import print_function, division, absolute_import

from ramploader import RampLoader
from ..images.plainrampimage import PlainRampImage
from ..core.defaults import MAX_TIME_SLICES


# catools
try:
    import cothread.catools
    _NO_CATOOLS_ = False
except ImportError:
    if __debug__:
        print("ImportError: I can not import the catools module!")
    _NO_CATOOLS_ = True


class PlainRampLoader(RampLoader):
    def __init__(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES):
        super(PlainRampLoader, self).__init__(pv_name, bipolar, max_time_slices)

    def reconfigure(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES):
        super(PlainRampLoader, self).reconfigure(pv_name, bipolar, max_time_slices)

    def _load(self, ramp_image):
        if self.pv_name == None:
            return None

        if ramp_image.image == None:
            return None

        pRamping = self.pv_name

        if __debug__ == True:
            print("Preparing to load plain ramp using PV:")
            print(pRamping)
            print("I am going to write the voltage list to PV: {0}...".format(self.pv_name))
            if _NO_CATOOLS_ == True:
                print("...but I see no catools module imported.")
            print("List len, points:", len(ramp_image.image))

        if _NO_CATOOLS_ == True:
            return None

        #Writing ramp table...
        cothread.catools.connect(pRamping, throw=False)
        caput_result = cothread.catools.caput(pRamping, ramp_image.image, wait=True, throw=False)

        if caput_result.errorcode == 192:
            reload(cothread.catools)
            print("caput failed: Virtual circuit disconnect.")
            print("Calibrating void lenses and attempting module reload...")
            print("Calculating force parameters and attempting caput...")
            caput_result = cothread.catools.caput(pRamping, ramp_image.image, wait=True, throw=False)

        if caput_result.ok != True:
            print(''.join(["My write to CA has failed (code ", str(caput_result.errorcode), ")"]))
            return None

        print("caput successful.")
        return 0

    def load_from_list(self, max_delta_list, points_list):
        """Load ramps from list"""
        ramp_image = PlainRampImage(self.bipolar, self.max_time_slices)
        ramp_image.get(max_delta_list, points_list)
        return self._load(ramp_image)

    @classmethod
    def is_loader_for(cls, ltype):
        return ltype.lower() == 'plain'
