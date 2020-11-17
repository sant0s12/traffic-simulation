import sys
import pygame
import random
import numpy as np
from driverModel import Driver, ModelParams
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 100

SIZE = WIDTH, HEIGHT = 1000, 100
SCREEN = pygame.display.set_mode(SIZE)

CLOCK = pygame.time.Clock()

class Car(pygame.sprite.Sprite):
    """Car game object
    Args:
        screen: pygame screen
        road: road object to later get the car in front
        startpos: starting position in screen coords
        speed: desired speed
    """

    def __init__(self, modelParams: ModelParams, road: 'Road', startpos: list, start_v: float):
        super(Car, self).__init__()
        self.surface = pygame.Surface((modelParams.length, 2))
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()

        self.pos = startpos
        self.pos_back = self.pos[0] - modelParams.length / 2
        self.pos_front = self.pos[0] + modelParams.length / 2
        self.rect.center = startpos

        self.road = road
        self.v = start_v

        # Hidden values to not share state
        self.__pos = list(startpos)
        self.__v = start_v

        self.driver = Driver(modelParams=modelParams)

    def __calcLaneChange(self, left, carFrontNow, carFrontChange, carBackChange):
        s_before = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * WIDTH
        s_before = max(0.000000001, s_before)
        other_v_before = carFrontNow.v if carFrontNow is not None else self.v

        s_after = (carFrontChange.pos_back - self.pos_front) if carFrontChange is not None else 2 * WIDTH
        s_after = max(0.000000001, s_after)
        other_v_after = carFrontChange.v if carFrontChange is not None else self.v

        if carBackChange is None:
            disadvantage = 0
            accel_behind_after = 0
        else:
            s_behind_before = (carFrontChange.pos_back - carBackChange.pos_front) if carFrontChange is not None else 2 * WIDTH
            other_v_behind_before = carFrontChange.v if carFrontChange is not None else carBackChange.v

            s_behind_after = (self.pos_back - carBackChange.pos_front)
            other_v_behind_after = self.v

            disadvantage, accel_behind_after = carBackChange.driver.disadvantageAndSafety(carBackChange.v, s_behind_before, other_v_behind_before, s_behind_after, other_v_behind_after)

        change = self.driver.changeLane(left=left, v=self.v, distFrontBefore=s_before, velFrontBefore=other_v_before, distFrontAfter=s_after, velFrontAfter=other_v_after, disadvantageBehindAfter=disadvantage, accelBehindAfter=accel_behind_after)

        return change

    def updateLocal(self):
        """
        Update local state
        """

        carFrontNow = None
        carFrontLeft = None
        carFrontRight = None
        carBackLeft = None
        carBackRight = None
        for car in self.road.carlist:
            if car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1]:
                carFrontNow = car if (carFrontNow is None or car.pos[0] < carFrontNow.pos[0]) else carFrontNow
            if (self.pos[1] is not road.bottomlane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                # Front right
                carFrontRight = car if (carFrontRight is None or car.pos[0] < carFrontRight.pos[0]) else carFrontRight
                pass
            if (self.pos[1] is not road.bottomlane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] + self.road.lanewidth):
                # Back right
                carBackRight = car if (carBackRight is None or car.pos[0] > carBackRight.pos[0]) else carBackRight
            if (self.pos[1] is not road.toplane and car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                # Front left
                carFrontLeft = car if (carFrontLeft is None or car.pos[0] < carFrontLeft.pos[0]) else carFrontLeft
            if (self.pos[1] is not road.toplane and car.pos[0] < self.pos[0] and car.pos[1] == self.pos[1] - self.road.lanewidth):
                # Back left
                carBackLeft = car if (carBackLeft is None or car.pos[0] > carBackLeft.pos[0]) else carBackLeft
            else: continue

        # Before this section of the code is run, the global and local state is the same, so e.g.
        # speed and __speed can be used interchangeably on the right hand side of the assignment

        # Change lanes
        changeLeft = self.__calcLaneChange(left=True, carFrontNow=carFrontNow, carFrontChange=carFrontLeft, carBackChange=carBackLeft)
        changeRight = self.__calcLaneChange(left=False, carFrontNow=carFrontNow, carFrontChange=carFrontRight, carBackChange=carBackRight)

        # Update local position
        self.__pos[0] += (self.v)/FPS

        if changeRight and self.pos[1] != self.road.bottomlane:
            self.__pos[1] += self.road.lanewidth
        elif changeLeft and self.pos[1] != self.road.toplane:
            self.__pos[1] -= self.road.lanewidth

        # Update local speed
        s = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * WIDTH
        s = max(0.000000001, s)
        other_v = carFrontNow.v if carFrontNow is not None else self.v
        self.__v += self.driver.getAccel(v=self.v, other_v=other_v, s=s) / FPS
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

    def draw(self):
        """
        Draw onto the screen
        """

        self.road.screen.blit(self.surface, self.rect)

class Road:
    """Road object to keep track of all the cars, create and destroy them when they are outside the screen

    Args:
        screen: pygame screen
        position: position of the middle of the top most lane
        lanes: amount of lanes
        lanewidth: width of the lanes
        frequency: car creation frequency
        avg_speed: average car speed
        speed_sigma: standard deviation in car speed
    """

    def __init__(self, screen, position, lanes=2, lanewidth=5, frequency=1, avg_speed=30, speed_sigma=10):
        self.screen = screen

        self.frequency = frequency
        self.ticks = frequency # Ticks since last car creation

        self.position = position
        self.lanes = lanes
        self.lanewidth = lanewidth
        self.toplane = self.position[1] # Position of top lane
        self.bottomlane = self.toplane + lanewidth * (lanes - 1)

        self.carlist: list[Car] = [] # List of cars on the load
        self.avg_speed = avg_speed
        self.speed_sigma = speed_sigma

    def update(self):
        """
        Update create cars and update all the cars in the list
        """

        # Create car with given frequency
        self.ticks += 1
        if FPS/self.ticks <= self.frequency:
            self.ticks = 0

            # Select random lane
            lane = random.choice(range(self.lanes)) * self.lanewidth
            v = np.random.normal(self.avg_speed, self.speed_sigma)

            params = ModelParams(v_0=v, s_0=2, s_1=0, T=1.6, a=0.73, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
            newCar = Car(modelParams=params, road=self, startpos=[self.position[0], self.position[1]], start_v=v)
            self.carlist.append(newCar)

        for car in self.carlist:
            car.updateLocal()

        for car in self.carlist:
            car.updateGlobal()
            if car.rect.left > WIDTH + 100:
                self.carlist.remove(car)
                #del car
            else: car.draw()

if __name__ == "__main__":
    road = Road(SCREEN, (0, HEIGHT/2), lanewidth=5, frequency=0.5, lanes=2)

    randomCar = None

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        SCREEN.fill(BLACK)
        road.update()

        if len(road.carlist) > 0:
            if randomCar is None: randomCar = road.carlist[0]
            elif randomCar not in road.carlist:
                randomCar = random.choice(road.carlist)

            randomCar.surface.fill((255,0,0))
            randomCar.draw()
            randomCar.v = 10
            randomCar.surface.fill(WHITE)


            print(randomCar.v * 3.6)

        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        CLOCK.tick(FPS)
