from __future__ import print_function, division, absolute_import

from ..core.defaults import MAX_TIME_SLICES


class RampLoader(object):
    """Loads a ramp from the file or list to the hardware"""
    def __init__(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES):
        self.pv_name = pv_name
        self.bipolar = bipolar
        self.max_time_slices = max_time_slices

    def reconfigure(self, pv_name, bipolar, max_time_slices=MAX_TIME_SLICES):
        self.pv_name = pv_name
        self.bipolar = bipolar
        self.max_time_slices = max_time_slices

    def _parse_file(self, file_name):
        with open(file_name) as in_file:
                contents = in_file.readlines()

        try:
            max_delta = float(contents.pop(0))
        except:
            print("Failed to retrieve max delta parameter (must be on line 1).")
            return None, None

        table = []

        for i, line in enumerate(contents):
            try:
                line = line.lstrip()
                if (line[0] == '#'):
                    continue
                pair = line.split()
                table.append((int(pair[0]), float(pair[1])))
                if (int(pair[0]) == self.max_time_slices):
                    break
            except:
                print("Failed to retrieve ramp key points. Check line {0}".format(i + 2))
                return None, None

        #return __debug__delta_1_list_, __debug__points_1_list_
        return max_delta, table

    def load_from_list(self, max_delta_list, points_list):
        """Load ramps from list"""
        pass

    def load_from_file(self, file_name):
        """Load ramps from file"""
        try:
            with open(file_name):
                pass
        except IOError:
            if __debug__ == True:
                print("Unable to open file for loading.")
            return None
        max_delta, points_list = self._parse_file(file_name)
        return self.load_from_list(max_delta, points_list)
