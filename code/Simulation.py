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

        def __init__(self, modelParams: ModelParams, road: 'Road', startpos: list, start_v: float=None):
            super(Simulation.Car, self).__init__()
            self.surface = pygame.Surface((modelParams.length, 2))
            self.surface.fill(WHITE)
            self.rect = self.surface.get_rect()

            self.pos = startpos
            self.pos_back = self.pos[0] - modelParams.length / 2
            self.pos_front = self.pos[0] + modelParams.length / 2
            self.rect.center = startpos

            self.road = road
            self.v = start_v if start_v is not None else modelParams.v_0

            # Hidden values to not share state
            self.__pos = list(startpos)
            self.__v = start_v
            self.__accel = 0.

            self.driver = Driver(modelParams=modelParams)

        def __calcLaneChange(self, left, carFrontNow, carFrontChange, carBackChange):
            s_before = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * self.road.length # Distance to the car in front
            other_v_before = carFrontNow.v if carFrontNow is not None else self.v                                   # Speed of the car in front

            s_after = (carFrontChange.pos_back - self.pos_front) if carFrontChange is not None else 2 * self.road.length # Same as above but after the change
            other_v_after = carFrontChange.v if carFrontChange is not None else self.v

            if carBackChange is None:
                disadvantage = 0
                accel_behind_after = 0
            else:
                s_behind_before = (carFrontChange.pos_back - carBackChange.pos_front) if carFrontChange is not None else 2 * self.road.length
                other_v_behind_before = carFrontChange.v if carFrontChange is not None else carBackChange.v

                s_behind_after = (self.pos_back - carBackChange.pos_front)
                other_v_behind_after = self.v

                disadvantage, accel_behind_after = carBackChange.driver.disadvantageAndSafety(carBackChange.v, s_behind_before, other_v_behind_before, s_behind_after, other_v_behind_after)

            change = self.driver.changeLane(left=left, v=self.v, distFrontBefore=s_before, velFrontBefore=other_v_before, distFrontAfter=s_after, velFrontAfter=other_v_after, disadvantageBehindAfter=disadvantage, accelBehindAfter=accel_behind_after)

            safeBack = carBackChange.pos_front < self.pos_back if carBackChange is not None else True
            safeFront = carFrontChange.pos_back > self.pos_front if carFrontChange is not None else True

            return change and safeBack and safeFront

        def getCarsAround(self):
            """Get other Cars around this Car

            Returns: Dict with:
                frontNow: current Car in front of this Car
                frontLeft: front left Car
                frontRight: front right Car
                backLeft: back left Car
                backRight: back right Car
            """

            carFrontNow = None
            carFrontLeft = None
            carFrontRight = None
            carBackLeft = None
            carBackRight = None

            for car in self.road.carlist:
                if car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1]:
                    carFrontNow = car if (carFrontNow is None or car.pos[0] < carFrontNow.pos[0]) else carFrontNow
                if (self.pos[1] is not self.road.bottomlane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                    # Front right
                    carFrontRight = car if (carFrontRight is None or car.pos[0] < carFrontRight.pos[0]) else carFrontRight
                    pass
                if (self.pos[1] is not self.road.bottomlane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                    # Back right
                    carBackRight = car if (carBackRight is None or car.pos[0] > carBackRight.pos[0]) else carBackRight
                if (self.pos[1] is not self.road.toplane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                    # Front left
                    carFrontLeft = car if (carFrontLeft is None or car.pos[0] < carFrontLeft.pos[0]) else carFrontLeft
                if (self.pos[1] is not self.road.toplane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                    # Back left
                    carBackLeft = car if (carBackLeft is None or car.pos[0] > carBackLeft.pos[0]) else carBackLeft
                else: continue

            return {"frontNow": carFrontNow, "frontLeft": carFrontLeft, "frontRight": carFrontRight, "backLeft": carBackLeft, "backRight": carBackRight}

        def updateLocal(self, delta_t: float):
            """
            Update local state
            """

            carsAround = self.getCarsAround()
            carFrontNow = carsAround["frontNow"]
            carFrontLeft = carsAround["frontLeft"]
            carFrontRight = carsAround["frontRight"]
            carBackLeft = carsAround["backLeft"]
            carBackRight = carsAround["backRight"]

            # Before this section of the code is run, the global and local state is the same, so e.g.
            # v and __v can be used interchangeably on the right hand side of the assignment

            # Change lanes
            changeLeft = self.__calcLaneChange(left=True, carFrontNow=carFrontNow, carFrontChange=carFrontLeft, carBackChange=carBackLeft)
            changeRight = self.__calcLaneChange(left=False, carFrontNow=carFrontNow, carFrontChange=carFrontRight, carBackChange=carBackRight)


            # Update local position
            self.__pos[0] += (self.v) * delta_t

            if changeRight and self.pos[1] != self.road.bottomlane:
                self.__pos[1] += self.road.lanewidth
            elif changeLeft and self.pos[1] != self.road.toplane:
                self.__pos[1] -= self.road.lanewidth

            # Update local speed
            s = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * self.road.length
            s = max(0.000000001, s)
            other_v = carFrontNow.v if carFrontNow is not None else self.v
            self.__v = self.v
            self.__accel = self.driver.getAccel(v=self.v, other_v=other_v, s=s) * delta_t
            self.__v += self.__accel
            self.__v = max(self.__v, 0)

        def updateGlobal(self):
            """
            Update global state
            """

            self.pos = self.__pos.copy()
            self.pos_back = self.pos[0] - self.driver.modelParams.length / 2
            self.pos_front = self.pos[0] + self.driver.modelParams.length / 2

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

        def __init__(self, modelParamsList, position=(0, 0), lanes=2, lanewidth=5, length=1000, car_frequency=1):
            self.modelParamsList = modelParamsList
            self.car_frequency = car_frequency
            self.last_new_car_t = 1.0/car_frequency # Time since last car creation

            self.position = position
            self.length = length
            self.lanes = lanes
            self.lanewidth = lanewidth
            self.toplane = self.position[1] # Position of top lane
            self.bottomlane = self.toplane + lanewidth * (lanes - 1)

            self.carlist: list[Car] = [] # List of cars on the load

        def update(self, delta_t: float):
            """
            Update create cars and update all the cars in the list
            """

            # Create car with given frequency
            self.last_new_car_t += delta_t
            if self.last_new_car_t >= 1.0/self.car_frequency:
                self.last_new_car_t = 0

                # Select random lane
                lane = random.choice(range(self.lanes)) * self.lanewidth

                params = random.choice(self.modelParamsList)
                newCar = Simulation.Car(modelParams=params, road=self, startpos=[self.position[0], self.position[1] + lane])
                self.carlist.append(newCar)

            for car in self.carlist:
                car.updateLocal(delta_t)

            for car in self.carlist:
                car.updateGlobal()
                if car.rect.left > self.length + 100:
                    self.carlist.remove(car)

        def draw(self, screen):
            for car in self.carlist:
                car.draw(screen)

    def __init__(self, modelParamsList: list, roadPosition=(0, 0), roadLength=1000, lanewideness =20, lanes_amt = 2, car_frequency=1, delta_t=0.1):
        self.modelParamsList = modelParamsList
        self.delta_time = delta_t
        self.road = Simulation.Road(modelParamsList=modelParamsList, position=roadPosition, lanewidth=lanewideness, car_frequency=car_frequency, lanes=lanes_amt)

    def step(self):
        self.road.update(delta_t=self.delta_time)
        return self.road.carlist

    def run(self, time: float):
        data = []
        for t in tqdm(np.arange(0, time, self.delta_time)):
            data.append([car.serialize() for car in self.step()])

        return data
