class Driver:
    """Driver Class to following the Intelligent Driver Model

    This class models our divers in the simulation using the provided formulas int the paper.

    Args:
        v: Starting velocity
        v_0: Desired velocity
        T: Safe time headway
        a: Maximum acceleration
        b: Desierd acceleration
        delta: Acceleration exponent
        s_0: Jam distance
        s_1: Jam Distance
        l: Vehicle length (l=1/p_max)
    """

    def __init__(self, v, v_0, T, a, b, delta, s_0, s_1, l):
        self.v = v
        self.v_0 = v_0
        self.T = T
        self.a = a
        self.b = b
        self.delta = delta
        self.s_0 = s_0
        self.s_1 = s_1
        self.l = l

    def __s_star(self, delta_v):
        s_star = (self.s_0
                + self.s_1 * sqrt(self.v/self.v_0)
                + self.T * self.v
                + (self.v + delta_v) / (2 * sqrt(self.a * self.b)))
        return s_star

    def getAccel(self, otherDriver: Driver):
        """Get current acceleration
        Args:
            otherDriver: Driver in front of this driver
        """

        delta_v = self.v - otherDriver.v
        s = 0 # TODO: Gap to the car in front
        s_star = self.__s_star(delta_v)

        accel = (self.a * (1 - pow(self.v/self.v_0, self.delta) - pow(s_star/s, 2)))

        return accel


