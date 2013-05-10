import struct
import numpy as np
from rampimage import RampImage


class PlainRampImage(RampImage):
    """Represents a voltage image of ramp list that can be loaded into the IOC"""
    def __init__(self, bipolar, max_time_slices):
        super(PlainRampImage, self).__init__(bipolar, max_time_slices)
        
        self.image = None

    def _interpolate_ramps(self, ramp_list):
        """Fill all missing voltage points with interpolated data."""
        if ramp_list.ramps != None:
            ramps = ramp_list.ramps
            table = []
            u2 = 0
            for ramp in ramps:
                for i in range(0, len(ramp.points) - 1):
                    t1 = ramp.points[i][0]
                    t2 = ramp.points[i + 1][0]
                    u1 = ramp.points[i][1]
                    u2 = ramp.points[i + 1][1]

                    delta = float(u2 - u1) / float(t2 - t1)

                    value = u1

                    for dummy in range(t1, t2):
                        table.append(value)
                        value = value + delta
            table.append(u2)
            return table
        else:
            return None

    def _get(self, ramp_list):
        """Pack human-readable voltage table to IOC-friendly float array."""
        if ramp_list != None:
            table = self._interpolate_ramps(ramp_list)
            if table == None:
                return None
            self.image = table
        else:
            self._invalidate()
        return self.image
