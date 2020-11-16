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
        thr: threshold for lane change
        p: politeness <1
    """

    def __init__(self, v: float, v_0: float, T: float, a: float, b: float, delta: float, s_0: float, s_1: float, l: float, thr: float, p: float):
        self.v = v
        self.v_0 = v_0
        self.T = T
        self.a = a
        self.b = b
        self.delta = delta
        self.s_0 = s_0
        self.s_1 = s_1
        self.l = l
        self.thr = thr
        self.p = p

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
            other_v: other velocity
        """

        delta_v = self.v - other_v
        s_star = self.__s_star(delta_v)

        accel = (self.a * (1 - math.pow(self.v/self.v_0, self.delta) - math.pow(s_star/s, 2)))

        return accel

    def disadvantageAndSafety(self, distOtherBefore: float, velOtherBefore:float, distOtherAfter:float, velOtherAfter: float):
        accelAfter = self.getAccel(distOtherBefore, velOtherAfter)
        accelBefore = self.getAccel(distOtherBefore, velOtherBefore)
        return (accelBefore - accelAfter, accelAfter)

    def changeLane(self, left:bool, distFrontBefore: float, velFrontBefore:float, distFrontAfter:float, velFrontAfter: float, disadvantageBehindAfter:float, accelBehindAfter:float):       
        accelAfter = self.getAccel(distFrontBefore, velFrontAfter)
        accelBefore = self.getAccel(distFrontBefore, velFrontBefore)
        advantage = accelAfter - accelBefore
        incentive = advantage > self.p * (disadvantageBehindAfter) + self.thr
        safe = accelBehindAfter > -self.T
        return incentive & safe
