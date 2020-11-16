import math
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

    def __init__(self, v: float, v_0: float, T: float, a: float, b: float, delta: float, s_0: float, s_1: float, l: float):
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
                + self.s_1 * math.sqrt(self.v/self.v_0)
                + self.T * self.v
                + (self.v + delta_v) / (2 * math.sqrt(self.a * self.b)))
        return s_star

    def updateSpeed(self, s: float, other_v: float):
        accel = self.getAccel(s, other_v)
        self.v += accel
        self.v = max(0, self.v)

        return self.v

    def getAccel(self, s: float, other_v: float):
        """Get current acceleration
        Args:
            s: Distance to the car in front
        """

        delta_v = self.v - other_v
        s_star = self.__s_star(delta_v)

        accel = (self.a * (1 - math.pow(self.v/self.v_0, self.delta) - math.pow(s_star/s, 2)))

        return accel

    def __changeLaneLeft(self, otherDriverBefore: 'Driver', otherDriverAfter: 'Driver'):
        accelAfter = self.getAccel(otherDriverAfter)
        accelBefore = self.getAccel(otherDriverBefore)
        return false

    def __changeLaneRight(self, otherDriverBefore: 'Driver', otherDriverAfter: 'Driver'):
        accelAfter = self.getAccel(otherDriverAfter)
        accelBefore = self.getAccel(otherDriverBefore)
        return false

    def changeLane(self, otherDriverBefore: 'Driver', otherDriverAfterRight: 'Driver', otherDriverAfterLeft: 'Driver'):
        changeRight = self.__changeLaneRight(otherDriverBefore=otherDriverBefore, otherDriverAfter=otherDriverAfterRight)
        changeLeft = self.__changeLaneLeft(otherDriverBefore=otherDriverBefore, otherDriverAfter=otherDriverAfterLeft)

        if changeRight: return 1
        if changeLeft: return -1
        else: return 0

