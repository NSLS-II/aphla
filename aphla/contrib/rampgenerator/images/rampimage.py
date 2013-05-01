from ..core.defaults import VOLTAGE_RANGE, CONVERT_COEFF
from ..core.ramplist import RampList


class RampImage(object):
    def __init__(self, bipolar, max_time_slices):
        self.bipolar = bipolar
        self.max_time_slices = max_time_slices

        self.voltage_range = VOLTAGE_RANGE
        self.convert_coeff = CONVERT_COEFF

        self.image = None

    def _invalidate(self):
        self.image = None

    def _get(self, ramp_list):
        pass

    def get(self, max_delta_list, points_list):
        ramp_list = RampList(self.bipolar, self.max_time_slices)
        ramp_list.extract(max_delta_list, points_list)
        return self._get(ramp_list)
