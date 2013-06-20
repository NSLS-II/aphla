from ramp import Ramp


class RampList(object):
    """Represents a list of ramps extracted from the given list"""
    def __init__(self, bipolar, max_time_slices):
        self.bipolar = bipolar
        self.max_time_slices = max_time_slices

        self.ramps = None

    def _invalidate(self):
        self.ramps = None

    def _extract(self, zipped_lists):
        self.ramps = []
        for max_delta, points in zipped_lists:
            ramp = Ramp(self.bipolar, self.max_time_slices)
            if ramp.construct(max_delta, points) != None:
                self.ramps.append(ramp)
            else:
                self._invalidate()
                break
        return self.ramps

    def extract(self, max_delta_list, points_list):
        try:
            #if type(max_delta_list) != list:
            if not isinstance(max_delta_list, list):
                max_delta_list = [max_delta_list]

            single_mode = True
            for item in points_list:
                #if type(item) == list:
                if isinstance(item, list):
                    single_mode = False
                    break
            if single_mode == True:
                points_list = [points_list]
        except:
            return None

        return self._extract(zip(max_delta_list, points_list))
