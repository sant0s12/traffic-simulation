import math

class ModelParams:
    """Class to store the IDM parameters

    Args:
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

    def __init__(self, v_0: float, s_0: float, s_1: float, T: float, a: float, b: float, delta: float, length: float, thr: float, pol: float):
        self.v_0 = v_0
        self.s_0 = s_0
        self.s_1 = s_1
        self.T = T
        self.a = a
        self.b = b
        self.delta = delta
        self.length = length
        self.thr = thr
        self.pol = pol

class Driver:
    """Driver Class to following the Intelligent Driver Model

    This class models our divers in the simulation using the provided formulas int the paper.

    Args:
        v: Starting velocity
        modelParams: model parameters
    """

    def __init__(self, modelParams: ModelParams):
        self.modelParams = modelParams

    def __s_star(modelParams: ModelParams, v, delta_v):
        s_star = (modelParams.s_0
                + modelParams.s_1 * math.sqrt(v/modelParams.v_0)
                + modelParams.T * v
                + (v + delta_v) / (2 * math.sqrt(modelParams.a * modelParams.b)))

        return s_star

    def getAccel(self, v, other_v, s):
        delta_v = v - other_v
        s_star = Driver.__s_star(modelParams=self.modelParams, v=v, delta_v=delta_v)
        accel = (self.modelParams.a * (1 - math.pow(v/self.modelParams.v_0, self.modelParams.delta) - math.pow(s_star/s, 2)))

        return accel

    def disadvantageAndSafety(self, v:float, distOtherBefore: float, velOtherBefore:float, distOtherAfter:float, velOtherAfter: float):
        accelAfter = self.getAccel(v, velOtherAfter, distOtherBefore)
        accelBefore = self.getAccel(v, velOtherBefore, distOtherBefore)
        return (accelBefore - accelAfter, accelAfter)

    def changeLane(self, left: bool, v: float, distFrontBefore: float, velFrontBefore:float, distFrontAfter:float, velFrontAfter: float, disadvantageBehindAfter:float, accelBehindAfter:float):
        accelAfter = self.getAccel(v, velFrontAfter, distFrontBefore)
        accelBefore = self.getAccel(v, velFrontBefore, distFrontBefore)
        advantage = accelAfter - accelBefore
        incentive = advantage > self.modelParams.pol * disadvantageBehindAfter + self.modelParams.thr
        safe = accelBehindAfter > -self.modelParams.b
        return (incentive) & safe
