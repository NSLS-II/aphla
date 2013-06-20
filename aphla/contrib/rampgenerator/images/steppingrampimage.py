import collections
import struct
import numpy as np
from rampimage import RampImage


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring) and not isinstance(el, tuple):
            for sub in flatten(el):
                yield sub
        else:
            yield el


def get_pack_len(dtype):
    return {
                'unsigned short': 2,
                'unsigned int': 4,
                'float': 4
            }[dtype]


def get_pack_format(dtype):
    return {
                'unsigned short': 'H',
                'unsigned int': 'I',
                'float': 'f'
            }[dtype]
            

class SteppingRampImage(RampImage):
    """Represents a binary image of ramp list that can be loaded into the hardware"""
    def __init__(self, bipolar, max_time_slices, max_key_stones):
        super(SteppingRampImage, self).__init__(bipolar, max_time_slices)
        
        self.max_key_stones = max_key_stones

        self._length_pack_type_ = 'unsigned int'
        self._time_pack_type_ = 'unsigned short'
        self._voltage_pack_type_ = 'unsigned int'

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

    def _get_data_repr(self, pack_type, data):
        return reversed(struct.pack(pack_type, data))
        # Smart-assed:
        #return struct.pack( pack_type, data )[::-1]

    def _convert_voltage(self, voltage):
        return self._voltage_to_code(voltage)

    def _get(self, ramp_list):
        """Pack the ramp list to hardware-friendly byte array."""
        if ramp_list.ramps != None:
            ramps = ramp_list.ramps
            lengths = [len(ramp.points) for ramp in ramps]
            if sum(lengths) > self.max_key_stones:
                print "The image is too long to fit in one MTU. Soz."
                self._invalidate()
                return self.image
            voltages = [voltage for time, voltage in flatten([ramp.points for ramp in ramps])]
            times = [time for time, voltage in flatten([ramp.points for ramp in ramps])]

            lengths_pack_len = get_pack_len(self._length_pack_type_)
            voltages_pack_len = get_pack_len(self._voltage_pack_type_)
            times_pack_len = get_pack_len(self._time_pack_type_)

            self.image = np.zeros((voltages_pack_len + times_pack_len) * sum(lengths) + lengths_pack_len * len(lengths), dtype=np.uint8)

            lengths_pack_type = get_pack_format(self._length_pack_type_)
            voltages_pack_type = get_pack_format(self._voltage_pack_type_)
            times_pack_type = get_pack_format(self._time_pack_type_)

            counter = 0

            for item in lengths:
                packed = self._get_data_repr(lengths_pack_type, item)
                for value in packed:
                    self.image[counter] = ord(value)
                    counter += 1

            for item in voltages:
                packed = self._get_data_repr(voltages_pack_type, self._convert_voltage(item))
                for value in packed:
                    self.image[counter] = ord(value)
                    counter += 1

            for item in times:
                packed = self._get_data_repr(times_pack_type, item)
                for value in packed:
                    self.image[counter] = ord(value)
                    counter += 1
        else:
            self._invalidate()
        return self.image