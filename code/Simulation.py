import sys
import pygame
import random
import numpy as np
from tqdm import tqdm
from DriverModel import Driver, ModelParams

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

class Simulation:
    """This class represents the whole simulation and contains the Road and Car objects

    Args:
        TODO
    """

    class Car(pygame.sprite.Sprite):
        """Car game object

        Args:
            screen: pygame screen
            road: road object to later get the car in front
            startpos: starting position in screen coords
            start_v: initial speed when spawned
        """

        def __init__(self, model_params: ModelParams, road: 'Road', startpos: list, start_v: float=None):
            super(Simulation.Car, self).__init__()
            self.surface = pygame.Surface((model_params.length, 2))
            self.surface.fill(WHITE)
            self.rect = self.surface.get_rect()

            self.pos = startpos
            self.pos_back = self.pos[0] - model_params.length / 2
            self.pos_front = self.pos[0] + model_params.length / 2
            self.rect.center = startpos

            self.road = road
            self.v = start_v if start_v is not None else model_params.v_0

            # Hidden values to not share state
            self.__pos = list(startpos)
            self.__v = start_v
            self.__accel = 0.

            self.driver = Driver(model_params=model_params)

        def __calc_lane_change(self, left, car_front_now, car_front_change, car_back_change):
            s_before = (car_front_now.pos_back - self.pos_front) if car_front_now is not None else 2 * self.road.length # Distance to the car in front
            other_v_before = car_front_now.v if car_front_now is not None else self.v                                   # Speed of the car in front

            s_after = (car_front_change.pos_back - self.pos_front) if car_front_change is not None else 2 * self.road.length # Same as above but after the change
            other_v_after = car_front_change.v if car_front_change is not None else self.v

            if car_back_change is None:
                disadvantage = 0
                accel_behind_after = 0
            else:
                s_behind_before = (car_front_change.pos_back - car_back_change.pos_front) if car_front_change is not None else 2 * self.road.length
                other_v_behind_before = car_front_change.v if car_front_change is not None else car_back_change.v

                s_behind_after = (self.pos_back - car_back_change.pos_front)
                other_v_behind_after = self.v

                disadvantage, accel_behind_after = car_back_change.driver.disadvantage_and_safety(car_back_change.v, s_behind_before, other_v_behind_before, s_behind_after, other_v_behind_after)

            change = self.driver.change_lane(left=left, v=self.v, dist_front_before=s_before, vel_front_before=other_v_before, dist_front_after=s_after, vel_front_after=other_v_after, disadvantage_behind_after=disadvantage, accel_behind_after=accel_behind_after)

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

        def updateLocal(self, delta_t: float):
            """
            Update local state
            """

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

            if change_right and self.pos[1] != self.road.bottomlane:
                self.__pos[1] += self.road.lanewidth
            elif change_left and self.pos[1] != self.road.toplane:
                self.__pos[1] -= self.road.lanewidth

            # Update local speed
            s = (car_front_now.pos_back - self.pos_front) if car_front_now is not None else 2 * self.road.length
            s = max(0.000000001, s)
            other_v = car_front_now.v if car_front_now is not None else self.v
            self.__v = self.v
            self.__accel = self.driver.get_accel(v=self.v, other_v=other_v, s=s) * delta_t
            self.__v += self.__accel
            self.__v = max(self.__v, 0)

        def updateGlobal(self):
            """
            Update global state
            """

            self.pos = self.__pos.copy()
            self.pos_back = self.pos[0] - self.driver.model_params.length / 2
            self.pos_front = self.pos[0] + self.driver.model_params.length / 2

            self.v = self.__v
            self.rect.center = self.pos.copy()

        def draw(self, screen):
            """
            Draw onto the screen
            """

            return screen.blit(self.surface, self.rect)

        def serialize(self):
            """Serialize the car

            Returns: Dict with:
            pos: position of the car
            accel: current acceleration
            rect: pygame rect (for displaying it later)
            surface: pygame surface (for displaying it later)
            """
            return {'pos': self.pos, 'v': self.v, 'accel': self.__accel, 'rect': self.rect.copy(), 'surface': self.surface.copy()}

    class Road:
        """Road object to keep track of all the cars, create and destroy them when they are outside the simulation bounds

        Args:
            position: position of the the top most lane
            lanes: amount of lanes
            lanewidth: width of the lanes
            car_frequency: car creation frequency
            length: road lenght
        """

        def __init__(self, model_params_list, position, lanes, lanewidth, length, car_frequency):
            self.model_params_list = model_params_list
            self.car_frequency = car_frequency
            self.last_new_car_t = 1.0/car_frequency # Time since last car creation

            self.position = position
            self.length = length
            self.lanes = lanes
            self.lanewidth = lanewidth
            self.toplane = self.position[1] # Position of top lane
            self.bottomlane = self.toplane + lanewidth * (lanes - 1)

            self.carlist: list[Car] = [] # List of cars on the load

        def spawn_car(self):
            """Create new car with the given frequency only if there is enough distance to the next car

            Returns: True if a car could be spawned, False otherwise
            """

            # Select random lane
            lane = random.choice(range(self.lanes)) * self.lanewidth
            params = random.choice(self.model_params_list)
            new_car = Simulation.Car(model_params=params, road=self, startpos=[self.position[0], self.position[1] + lane])

            car_front = new_car.get_cars_around()["frontNow"]

            if car_front is not None:
                t = (car_front.pos_back - new_car.pos_front) / new_car.v if new_car.v != 0 else new_car.driver.model_params.T
                clipping = (car_front.pos_back - new_car.pos_front) <= 0
            else:
                t = new_car.driver.model_params.T
                clipping = False

            if t >= new_car.driver.model_params.T and not clipping:
                self.carlist.append(new_car)
                return True
            else:
                return False

        def update(self, delta_t: float):
            """Create cars and update all the cars in the list
            """

            for car in self.carlist:
                car.updateLocal(delta_t)

            for car in self.carlist:
                car.updateGlobal()
                if car.rect.left > self.length + 100:
                    self.carlist.remove(car)

            self.last_new_car_t += delta_t
            if self.last_new_car_t >= 1.0/self.car_frequency and self.spawn_car():
                self.last_new_car_t = 0

        def draw(self, screen):
            for car in self.carlist:
                car.draw(screen)

    def __init__(self, model_params_list: list, road_position=(0, 0), road_length=1000, road_lanes=2, road_lane_width=5, car_frequency=1, delta_t=0.1):
        self.model_params_list = model_params_list
        self.delta_t = delta_t
        self.road = Simulation.Road(model_params_list=model_params_list, position=road_position, lanewidth=road_lane_width, car_frequency=car_frequency, lanes=road_lanes, length=road_length)

    def step(self):
        self.road.update(delta_t=self.delta_t)
        return self.road.carlist

    def run(self, time: float):
        data = []
        for t in tqdm(np.arange(0, time, self.delta_t)):
            data.append([car.serialize() for car in self.step()])

        return data

