from __future__ import print_function, division, absolute_import

from ramploader import RampLoader
from ..images.steppingrampimage import SteppingRampImage
from ..core.defaults import MAX_TIME_SLICES, MAX_KEY_STONES


# catools
try:
    #import cothread
    from cothread.catools import caput, connect
    _NO_CATOOLS_ = False
except ImportError:
    if __debug__:
        print("ImportError: I can not import the catools module!")
    _NO_CATOOLS_ = True


class SteppingRampLoader(RampLoader):
    """Loads a ramp from the file or list to the hardware"""
    def __init__(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES, max_key_stones=MAX_KEY_STONES):
        super(SteppingRampLoader, self).__init__(pv_name, bipolar, max_time_slices)

        self.max_key_stones = max_key_stones

    def reconfigure(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES, max_key_stones=MAX_KEY_STONES):
        super(SteppingRampLoader, self).reconfigure(pv_name, bipolar, max_time_slices)

        self.max_key_stones = max_key_stones

    def _load(self, ramp_image):
        if ramp_image.image == None or self.pv_name == None:
            return None

        if __debug__ == True:
            print("I am going to write the stepping binary image to PV: {0}...".format(self.pv_name))
            if _NO_CATOOLS_ == True:
                print("...but I see no catools module imported.")
            print("Image: ", ramp_image.image)
            print("Image len, bytes:", len(ramp_image.image))

        if _NO_CATOOLS_ == True:
            return None

        try:
            connect(self.pv_name, throw=False)
            caput(self.pv_name, ramp_image.image, wait=True)
        except:
            if __debug__ == True:
                print("My write to CA has failed.")
            return None

        return 0

    def load_from_list(self, max_delta_list, points_list):
        """Load ramps from list"""
        ramp_image = SteppingRampImage(self.bipolar, self.max_time_slices, self.max_key_stones)
        ramp_image.get(max_delta_list, points_list)
        return self._load(ramp_image)

    @classmethod
    def is_loader_for(cls, ltype):
        return ltype.lower() == 'stepping'
