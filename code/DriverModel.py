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
        fs: how many steps to wait if failing
        fp: failure probability per step per car
    """

    def __init__(self, v_0: float, s_0: float, s_1: float, T: float, a: float, b: float, delta: float, length: float, thr: float, pol: float, fs: int, fp: float):
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
        self.fs = fs
        self.fp = fp

class Driver:
    """Driver Class to following the Intelligent Driver Model

    This class models our divers in the simulation using the provided formulas int the paper.

    Args:
        v: Starting velocity
        modelParams: model parameters
    """

    def __init__(self, model_params: ModelParams):
        self.model_params = model_params

    def __s_star(model_params: ModelParams, v, delta_v):
        s_star = (model_params.s_0
                + model_params.s_1 * math.sqrt(v/model_params.v_0)
                + model_params.T * v
                + (v + delta_v) / (2 * math.sqrt(model_params.a * model_params.b)))

        return s_star

    def get_accel(self, v, other_v, s):
        delta_v = v - other_v
        s_star = Driver.__s_star(model_params=self.model_params, v=v, delta_v=delta_v)
        accel = (self.model_params.a * (1 - math.pow(v/self.model_params.v_0, self.model_params.delta) - math.pow(s_star/s, 2)))

        return accel

    def disadvantageAndSafety(self, v:float, distOtherBefore: float, velOtherBefore:float, distOtherAfter:float, velOtherAfter: float):
        accelAfter = self.getAccel(v, velOtherAfter, distOtherAfter)
        accelBefore = self.getAccel(v, velOtherBefore, distOtherBefore)
        return (accelBefore - accelAfter, accelAfter)

    def change_lane(self, left: bool, v: float, dist_front_before: float, vel_front_before:float, dist_front_after:float, vel_front_after: float, disadvantage_behind_after:float, accel_behind_after:float):
        delta = 0.2
        delta = delta if left else 0
        accel_after = self.get_accel(v, vel_front_after, dist_front_before)
        accel_before = self.get_accel(v, vel_front_before, dist_front_before)
        advantage = accel_after - accel_before
        incentive = advantage > self.model_params.pol * disadvantage_behind_after + self.model_params.thr + delta
        safe = accel_behind_after > -self.model_params.b
        return incentive & safe
