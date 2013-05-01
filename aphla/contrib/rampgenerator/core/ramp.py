class Ramp(object):
    """Represents a ramp that consists of key points descriptions"""
    def __init__(self, bipolar, max_time_slices):
        self.bipolar = bipolar
        self.max_time_slices = max_time_slices

        self.max_delta = None
        self.points = None

    def _invalidate(self):
        self.max_delta = None
        self.points = None

    def _verify_key_points(self):
        """Validate the key points pairs list."""
        if self.points == None:
            return 1

        errors = 0

        for i, pair in enumerate(self.points):
            t = int(pair[0])
            u = float(pair[1])
            if (t < 0) or (t > self.max_time_slices):
                print("Time stamp out of bounds at pair {0}: {1}".format(i + 1, pair))
                errors += 1
            if (self.bipolar == False) and (u < 0):
                print("Voltage is negative in unipolar mode at pair {0}: {1}".format(i + 1, pair))
                errors += 1

        if self.max_delta != None:
            max_slice_delta = float(self.max_delta) / self.max_time_slices

        for i in range(0, len(self.points) - 1):
            t1 = int(self.points[i][0])
            t2 = int(self.points[i + 1][0])
            u1 = float(self.points[i][1])
            u2 = float(self.points[i + 1][1])

            if (t2 < t1):
                print("Time stamp at reverse order at pairs {0}: {1} and {2}: {3}".format(i + 1, self.points[i], i + 2, self.points[i + 1]))
                errors += 1

            if (t1 == t2):
                print("Equal time stamps at pairs {0}: {1} and {2}: {3}".format(i + 1, self.points[i], i + 2, self.points[i + 1]))
                errors += 1
            elif self.max_delta != None:
                delta = float(u2 - u1) / float(t2 - t1)
                if abs(delta) > abs(max_slice_delta):
                    print("Ramp derivative ({0}) exceeds maximum delta ({1}) at pairs {2}: {3} and {4}: {5}".format(abs(delta), max_slice_delta, i + 1, self.points[i], i + 2, self.points[i + 1]))
                    errors += 1

        if (int(self.points[0][0]) != 0):
            print "Initial time stamp (0) not found: first is", self.points[0][0]
            errors += 1

        if (int(self.points[-1][0]) != self.max_time_slices - 1):
            print "Final time stamp (", self.max_time_slices - 1, ") not found: latest is", self.points[-1][0]
            errors += 1

        return errors

    def _verify(self):
        errors = self._verify_key_points()
        if (errors != 0):
            print "Verification failure:", errors, "error(s). Check mistakes above."
            self._invalidate()

    def construct(self, max_delta, points):
        try:
            self.max_delta = max_delta
            self.points = points

            if len(self.points) != 0:
                self._verify()
        except (TypeError, ValueError) as e:
            print "Exception caused by Ramp construction parameters: {0}.".format(e)
            self.points = None

        return self.points
