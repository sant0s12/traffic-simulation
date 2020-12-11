import warnings

import random

import numpy as np
from DriverModel import Driver

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Params:
    """Class to store the Car parameters, including IDM parameters

    Kwargs:
        If arg is passed as tuple, then first value is the average and second is the standard deviation (with cuttof at 2 sigma)

        v_0: Desired velocity
        s_0: Jam distance
        s_1: Jam Distance
        T: Safe time headway
        a: Maximum acceleration
        b: Desierd acceleration
        delta: Acceleration exponent
        length: Vehicle length
        thr: threshold for lane change
        pol: politeness <1
        fail_p: Probability of failure per step
        right_bias: Bias to switch to the right lane
        start_v: Starging speed when spawned
        fail_steps: Steps the car will be stationary
        spawn_weight: Defines the weighted probability that this car will spawn
    """

    def __init__(self, **kwargs):
        self.v_0 = kwargs.pop('v_0', (30, 1))
        self.s_0 = kwargs.pop('s_0', (2, 1))
        self.s_1 = kwargs.pop('s_1', 0)
        self.T = kwargs.pop('T', (1.5, 1))
        self.a = kwargs.pop('a', (2, 1))
        self.b = kwargs.pop('b', (3, 1))
        self.delta = kwargs.pop('delta', 4)
        self.length = kwargs.pop('length', (5, 1))
        self.thr = kwargs.pop('thr', 0.2)
        self.pol = kwargs.pop('pol', (0.5, 1))
        self.fail_p = kwargs.pop('fail_p', 0)
        self.right_bias = kwargs.pop('right_bias', 0.3)

        # Distribution never applied to these params
        self.start_v = kwargs.pop('start_v', None)
        self.fail_steps = kwargs.pop('fail_steps', 1)
        self.spawn_weight = kwargs.pop('spawn_weight', 10)

        if len(kwargs) > 0:
            for arg in kwargs.keys(): warnings.warn("Unexpected kwarg " + arg)

    def apply_dist(self):
        """Applies the distribution and returns a Params object with fixed values
        """
        
        # Make sure we get no negative values and that we cut off at 2 sigma (then the average will be chosen)
        def positive_normal(avg, dev):
            a = abs(np.random.normal(avg, dev))
            return a if avg-2*dev <= a <= avg+2*dev else avg

        v_0 = positive_normal(self.v_0[0], self.v_0[1]) if hasattr(self.v_0, '__getitem__') else self.v_0
        s_0 = positive_normal(self.s_0[0], self.s_0[1]) if hasattr(self.s_0, '__getitem__') else self.s_0
        s_1 = positive_normal(self.s_1[0], self.s_1[1]) if hasattr(self.s_1, '__getitem__') else self.s_1
        T = positive_normal(self.T[0], self.T[1]) if hasattr(self.T, '__getitem__') else self.T
        a = positive_normal(self.a[0], self.a[1]) if hasattr(self.a, '__getitem__') else self.a
        b = positive_normal(self.b[0], self.b[1]) if hasattr(self.b, '__getitem__') else self.b
        delta = positive_normal(self.delta[0], self.delta[1]) if hasattr(self.delta, '__getitem__') else self.delta
        length = positive_normal(self.length[0], self.length[1]) if hasattr(self.length, '__getitem__') else self.length
        thr = positive_normal(self.thr[0], self.thr[1]) if hasattr(self.thr, '__getitem__') else self.thr
        pol = positive_normal(self.pol[0], self.pol[1]) if hasattr(self.pol, '__getitem__') else self.pol
        fail_p = positive_normal(self.fail_p[0], self.fail_p[1]) if hasattr(self.fail_p, '__getitem__') else self.fail_p
        right_bias = positive_normal(self.right_bias[0], self.right_bias[1]) if hasattr(self.right_bias, '__getitem__') else self.right_bias

        start_v = self.start_v if self.start_v is not None else v_0
        fail_steps = self.fail_steps
        spawn_weight = self.spawn_weight

        return Params(v_0=v_0, s_0=s_0, s_1=s_1, T=T, a=a, b=b, delta=delta, length=length,
                      thr=thr, pol=pol, start_v=start_v, fail_p=fail_p, right_bias=right_bias, fail_steps=fail_steps, spawn_weight=spawn_weight)

class Car:
    """Car game object

    Args:
        screen: pygame screen
        road: Road object to later get the car in front
        startpos: Starting position in screen coords
    """

    def __init__(self, params: Params, road: 'Road', startpos):
        self.params = params.apply_dist()

        self.pos = startpos
        self.pos_back = self.pos[0] - self.params.length / 2
        self.pos_front = self.pos[0] + self.params.length / 2

        self.road = road
        self.v = self.params.start_v

        self.failing = False
        self.steps_left = self.params.fail_steps

        # Hidden values to not share state
        self.__pos = list(startpos)
        self.__v = self.params.start_v
        self.__accel = 0.

        self.driver = Driver(params=self.params)

    def __calc_lane_change(self, left, car_front_now, car_front_change, car_back_change):
        """Calculates if a car should change lanes

        Args:
            left: True if the lane change is to the left lane
            car_front_now: Car that is currently in front
            car_back_change: Car that will be in front after the change
            car_back_change: Car that will be in the back after the change

        Returns: True if the lane change should happen
        """

        s_before = (car_front_now.pos_back - self.pos_front) if car_front_now is not None else 2 * self.road.length # Distance to the car in front
        other_v_before = car_front_now.v if car_front_now is not None else self.v                                   # Speed of the car in front

        s_after = (car_front_change.pos_back - self.pos_front) if car_front_change is not None else 2 * self.road.length # Same as above but after the change
        other_v_after = car_front_change.v if car_front_change is not None else self.v

        if car_back_change is None: # If there is no car in front, set both to 0
            disadvantage = 0
            accel_behind_after = 0
        else:
            s_behind_before = (car_front_change.pos_back - car_back_change.pos_front) if car_front_change is not None else 2 * self.road.length
            other_v_behind_before = car_front_change.v if car_front_change is not None else car_back_change.v

            s_behind_after = (self.pos_back - car_back_change.pos_front)
            other_v_behind_after = self.v

            disadvantage, accel_behind_after = car_back_change.driver.disadvantage_and_safety(car_back_change.v, s_behind_before, other_v_behind_before, s_behind_after, other_v_behind_after)

        # Using the MOBIL model
        change = self.driver.change_lane(left=left, v=self.v, dist_front_before=s_before, vel_front_before=other_v_before, dist_front_after=s_after, vel_front_after=other_v_after, disadvantage_behind_after=disadvantage, accel_behind_after=accel_behind_after)

        # These extra conditions just make sure that cars would not collide if a lane change would to happen
        safeBack = car_back_change.pos_front < self.pos_back if car_back_change is not None else True
        safeFront = car_front_change.pos_back > self.pos_front if car_front_change is not None else True

        return change and safeBack and safeFront

    def get_cars_around(self):
        """Get other Cars around this Car

        Returns: Dict with:
            frontNow: current Car in front of this Car
            frontLeft: front left Car
            frontRight: front right Car
            backLeft: back left Car
            backRight: back right Car
        """

        car_front_now = None
        car_front_left = None
        car_front_right = None
        car_back_left = None
        car_back_right = None

        for car in self.road.carlist:
            if car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1]:
                car_front_now = car if (car_front_now is None or car.pos[0] < car_front_now.pos[0]) else car_front_now
            if (self.pos[1] is not self.road.bottomlane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                # Front right
                car_front_right = car if (car_front_right is None or car.pos[0] < car_front_right.pos[0]) else car_front_right
                pass
            if (self.pos[1] is not self.road.bottomlane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                # Back right
                car_back_right = car if (car_back_right is None or car.pos[0] > car_back_right.pos[0]) else car_back_right
            if (self.pos[1] is not self.road.toplane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                # Front left
                car_front_left = car if (car_front_left is None or car.pos[0] < car_front_left.pos[0]) else car_front_left
            if (self.pos[1] is not self.road.toplane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                # Back left
                car_back_left = car if (car_back_left is None or car.pos[0] > car_back_left.pos[0]) else car_back_left
            else: continue

        return {"frontNow": car_front_now, "frontLeft": car_front_left, "frontRight": car_front_right, "backLeft": car_back_left, "backRight": car_back_right}

    def update_local(self, delta_t: float):
        """
        Update local state
        """

        # If a car is currently failing or fails now by chance
        if self.failing or (np.random.random() < self.params.fail_p):

            self.failing = True
            if self.steps_left > 0:
                self.steps_left -= 1
            else:
                self.steps_left = self.params.fail_steps
                self.failing = False

        # Get cars around this one to perform calculations based on them
        cars_around = self.get_cars_around()
        car_front_now = cars_around["frontNow"]
        car_front_left = cars_around["frontLeft"]
        car_front_right = cars_around["frontRight"]
        car_back_left = cars_around["backLeft"]
        car_back_right = cars_around["backRight"]

        # Before this section of the code is run, the global and local state is the same, so e.g.
        # v and __v can be used interchangeably on the right hand side of the assignment

        # Change lanes
        change_left = self.__calc_lane_change(left=True, car_front_now=car_front_now, car_front_change=car_front_left, car_back_change=car_back_left)
        change_right = self.__calc_lane_change(left=False, car_front_now=car_front_now, car_front_change=car_front_right, car_back_change=car_back_right)


        # Update local position
        self.__pos[0] += (self.v) * delta_t

        # Don't jump outside of the road :)
        if change_right and self.pos[1] != self.road.bottomlane:
            self.__pos[1] += self.road.lanewidth
        elif change_left and self.pos[1] != self.road.toplane:
            self.__pos[1] -= self.road.lanewidth

        # Update local speed
        s = (car_front_now.pos_back - self.pos_front) if car_front_now is not None else 2 * self.road.length
        s = max(0.000000001, s) # s can't be 0 or it will break things so we make s smol
        other_v = car_front_now.v if car_front_now is not None else self.v
        self.__v = self.v
        self.__accel = self.driver.get_accel(v=self.v, other_v=other_v, s=s) * delta_t if not self.failing else 0
        self.__v += self.__accel
        self.__v = max(self.__v, 0) if not self.failing else 0

    def update_global(self):
        """
        Update global state
        """

        self.pos = self.__pos.copy()
        self.pos_back = self.pos[0] - self.driver.params.length / 2
        self.pos_front = self.pos[0] + self.driver.params.length / 2

        self.v = self.__v

    def serialize(self):
        """Serialize the car

        Returns:
            Dict with:
                pos: Position of the car
                v: Speed of the car
                accel: Acceleration of the car
                length: Length of the car
        """
        return {'pos': self.pos, 'v': self.v, 'accel': self.__accel, 'length': self.params.length}
