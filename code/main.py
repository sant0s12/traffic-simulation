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
        start_v: initial speed when spawned
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

    def __calcLaneChange(self, left: bool, carFrontNow: 'Car', carFrontChange: 'Car', carBackChange: 'Car'):
        """Calculate if car should change lane

        Args:
        left: True if the current lane change is a left lane change
        carFrontNow: current Car in front of this Car
        carFrontNow: Car that will be in front of this Car after the change
        carBackChange: Car that will be behind this Car after the cange

        Returns: True if the lane change should happen, False otherwise
        """
        s_before = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * WIDTH # Distance to the car in front
        other_v_before = carFrontNow.v if carFrontNow is not None else self.v                        # Difference in speed to the car in front

        s_after = (carFrontChange.pos_back - self.pos_front) if carFrontChange is not None else 2 * WIDTH # Same as above but after the change
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

        # Check that the cars will not intersect
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

        return {"frontNow": carFrontNow, "frontLeft": carFrontLeft, "frontRight": carFrontRight, "backLeft": carBackLeft, "backRight": carBackRight}

    def updateLocal(self):
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
        self.__pos[0] += (self.v)/FPS

        if changeRight and self.pos[1] != self.road.bottomlane:
            self.__pos[1] += self.road.lanewidth
        elif changeLeft and self.pos[1] != self.road.toplane:
            self.__pos[1] -= self.road.lanewidth

        # Update local speed
        s = (carFrontNow.pos_back - self.pos_front) if carFrontNow is not None else 2 * WIDTH
        s = max(0.000000001, s)
        other_v = carFrontNow.v if carFrontNow is not None else self.v
        self.__v = self.v
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

        return self.road.screen.blit(self.surface, self.rect)

class Road:
    """Road object to keep track of all the cars, create and destroy them when they are outside the screen

    Args:
        screen: pygame screen
        position: position of the middle of the top most lane
        lanes: amount of lanes
        lanewidth: width of the lanes
        frequency: car creation frequency (amount of cars / second)
        avg_speed: average car speed
        speed_sigma: standard deviation in car speed
    """

    def __init__(self, screen, position, lanes=2, lanewidth=5, frequency=1, avg_speed=30, speed_sigma=1):
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

            params = ModelParams(v_0=v, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
            newCar = Car(modelParams=params, road=self, startpos=[self.position[0], self.position[1] + lane], start_v=v)
            self.carlist.append(newCar)

        for car in self.carlist:
            car.updateLocal()

        for car in self.carlist:
            car.updateGlobal()
            if car.rect.left > WIDTH + 100:
                self.carlist.remove(car)
                #del car
            else: car.draw()

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

if __name__ == "__main__":
    road = Road(SCREEN, (0, HEIGHT/2), lanewidth=5, frequency=1, lanes=3, avg_speed=30, speed_sigma=1)

    debugCar = None

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for car in road.carlist:
                    if debugCar is None or dist(car.pos, mouse_pos) < dist(debugCar.pos, mouse_pos):
                        debugCar = car

        SCREEN.fill(BLACK)
        road.update()

        if debugCar is not None:

            for car in debugCar.getCarsAround().values():
                if car is None: continue
                car.surface.fill((0,0,255))
                car.draw()
                car.surface.fill(WHITE)

            # debugCar.v = 0
            debugCar.surface.fill((255,0,0))
            debugCar.draw()
            debugCar.surface.fill(WHITE)

            print("{} kmh out of {} kmh".format(debugCar.v * 3.6, debugCar.driver.modelParams.v_0 * 3.6))

        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        CLOCK.tick(FPS)
