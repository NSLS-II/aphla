import struct
import numpy as np
from rampimage import RampImage


class FullRampImage(RampImage):
    """Represents a binary image of ramp list that can be loaded into the hardware"""
    def __init__(self, bipolar, max_time_slices):
        super(FullRampImage, self).__init__(bipolar, max_time_slices)

        self.image = None

    def _voltage_to_code(self, voltage):
        """Convert human-readable float voltage value into hardware code

        Keyword arguments:
        voltage -- human-readable float voltage value
        """
        if self.bipolar == True:
            code = int((self.voltage_range + voltage) / (self.convert_coeff * 2.0))
        else:
            code = int(voltage / self.convert_coeff)
        return code

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
        """Pack human-readable voltage table to hardware-friendly byte array."""
        if ramp_list != None:
            table = self._interpolate_ramps(ramp_list)
            if table == None:
                return None
                
            
            #self.image = np.zeros(4 * len(table), dtype=np.uint8)
            self.image = np.zeros(4 * 10860, dtype=np.uint8)

            counter = 0
            for element in table:
                for value in reversed(struct.pack('i', self._voltage_to_code(element))):
                    self.image[counter] = ord(value)
                    counter = counter + 1
            
            self.image[0] = 255
            self.image[43436] = 255
            self.image[43437] = 255
            self.image[43438] = 255
            self.image[43439] = 255
            '''
            self.image = table
	        '''
            
        else:
            self._invalidate()
        return self.image
