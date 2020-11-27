import math

class Driver:
    """Driver Class to following the Intelligent Driver Model

    This class models our divers in the simulation using the provided formulas int the paper.

    Args:
        v: Starting velocity
        params: car parameters
    """

    def __init__(self, params):
        self.params = params

    def __s_star(params, v, delta_v):
        s_star = (params.s_0
                + params.s_1 * math.sqrt(v/params.v_0)
                + params.T * v
                + (v + delta_v) / (2 * math.sqrt(params.a * params.b)))

        return s_star

    def get_accel(self, v, other_v, s):
        delta_v = v - other_v
        s_star = Driver.__s_star(params=self.params, v=v, delta_v=delta_v)
        accel = (self.params.a * (1 - math.pow(v/self.params.v_0, self.params.delta) - math.pow(s_star/s, 2)))

        return accel

    def disadvantage_and_safety(self, v:float, dist_other_before: float, vel_other_before:float, dist_other_after:float, vel_other_after: float):
        accel_after = self.get_accel(v, vel_other_after, dist_other_after)
        accel_before = self.get_accel(v, vel_other_before, dist_other_before)
        return (accel_before - accel_after, accel_after)

    def change_lane(self, left: bool, v: float, dist_front_before: float, vel_front_before:float, dist_front_after:float, vel_front_after: float, disadvantage_behind_after:float, accel_behind_after:float):
        delta = 0.2
        delta = delta if left else 0
        accel_after = self.get_accel(v, vel_front_after, dist_front_before)
        accel_before = self.get_accel(v, vel_front_before, dist_front_before)
        advantage = accel_after - accel_before
        incentive = advantage > self.params.pol * disadvantage_behind_after + self.params.thr + delta
        safe = accel_behind_after > -self.params.b
        return incentive & safe
