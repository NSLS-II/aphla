from ramploader import RampLoader
from ..images.fullrampimage import FullRampImage
from ..core.defaults import MAX_TIME_SLICES


# catools
try:
    from cothread.catools import caput, caget, connect
    _NO_CATOOLS_ = False
except ImportError:
    if __debug__:
        print "ImportError: I can not import the catools module!"
    _NO_CATOOLS_ = True


class FullRampLoader(RampLoader):
    def __init__(self, pv_prefix, bipolar, channel_index, max_time_slices=MAX_TIME_SLICES):
        super(FullRampLoader, self).__init__(pv_prefix, bipolar, max_time_slices)

        self.channel_index = channel_index

    def reconfigure(self, pv_prefix, bipolar, channel_index, max_time_slices=MAX_TIME_SLICES):
        super(FullRampLoader, self).reconfigure(pv_prefix, bipolar, max_time_slices)

        self.table_index = channel_index

    def _load(self, ramp_image):
        if self.pv_name == None:
            return None

        if ramp_image.image == None:
            return None

        if self.channel_index == None:
            return None      

        pRamping = self.pv_name + 'Chan' + str(self.channel_index) + '-Asyn.BOUT'

        if __debug__ == True:
            print "Preparing to load full ramp in channel " + str(self.channel_index) + " using PV:"
            print pRamping
            print "Destination channel index is", self.channel_index
            print "I am going to write the binary image of full ramp to PV with prefix: {0}...".format(self.pv_name)
            if _NO_CATOOLS_ == True:
                print "...but I see no catools module imported."
            #print "Image: ", ramp_image.image
            print "Image len, bytes:", len(ramp_image.image)

        if _NO_CATOOLS_ == True:
            return None

        try:
            #Writing binary ramp table...
            connect(pRamping, throw=False)
            caput(pRamping, ramp_image.image, wait=True)

        except:
            if __debug__ == True:
                print "My write to CA has failed."
            return None

        return 0

    def load_from_list(self, max_delta_list, points_list):
        """Load ramps from list"""
        ramp_image = FullRampImage(self.bipolar, self.max_time_slices)
        ramp_image.get(max_delta_list, points_list)
        return self._load(ramp_image)

    @classmethod
    def is_loader_for(cls, ltype):
        return ltype.lower() == 'full'
