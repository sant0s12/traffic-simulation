import sys
import pygame
import random
import numpy as np
from driverModel import Driver
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
FPS = 60

size = width, height = 1000, 100
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

class Car(pygame.sprite.Sprite):
    """Car game object
    Args:
        screen: pygame screen
        road: road object to later get the car in front
        startpos: starting position in screen coords
        direction: direction of the car (for our purposes only straight lines)
    """
    def __init__(self, screen, road, startpos, speed: float):
        super(Car, self).__init__()
        self.surface = pygame.Surface((5, 2))
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()

        self.pos = list(startpos)
        self.rect.center = startpos

        self.screen = screen
        self.road: 'Road' = road
        self.speed = speed

        # Hidden values to not share state
        self.__pos = list(startpos)
        self.__speed = speed

        # Model takes "real values" (independent of FPS and scaling) 
        self.model = Driver(self.speed, self.speed, 1.6/FPS, 0.73, 1.67, 4, 2, 0, 5) # To be tweaked

    def updateLocal(self):
        """
        Move object along direction vector
        """

        carInFrontNow = None
        carInFrontLeft = None
        carInFrontRight = None
        for car in self.road.carlist:
            if car.pos[0] > self.pos[0] and car.pos[1] == self.pos[1]:
                carInFrontNow = car if (carInFrontNow is None or car.pos[0] < carInFrontNow.pos[0]) else carInFrontNow
            if (self.pos[1] is not road.bottomlane):
                pass
            if (self.pos[1] is not road.toplane):
                pass
            else: continue

        self.__pos[0] += (self.speed)/FPS
        self.__speed = self.model.updateSpeed((carInFrontNow.pos[0] - self.pos[0]) if carInFrontNow is not None else 100000, 
                                    carInFrontNow.speed if carInFrontNow is not None else self.speed)

    def updateGlobal(self):
        self.pos[0] = self.__pos[0]
        self.speed = self.__speed
        self.rect.center = self.pos.copy()

    def draw(self):
        """
        Draw onto the screen
        """

        screen.blit(self.surface, self.rect)

class Road:
    """Road object to keep track of all the cars, create and destroy them when they are outside the screen

    Args:
        screen: pygame screen
        position: position of the middle of the top most lane
        lanes: amount of lanes
        lanewidth: width of the lanes
        frequency: (more like deltaT at the moment) car creation frequency
    """

    def __init__(self, screen, position, lanes=2, lanewidth=5, frequency=1, avg_speed=200, speed_sigma=10):
        self.screen = screen

        self.frequency = frequency
        self.ticks = frequency

        self.position = position
        self.lanes = lanes
        self.lanewidth = lanewidth
        self.toplane = 0
        self.bottomlane = lanewidth * (lanes - 1)

        self.carlist: list[Car] = []
        self.avg_speed = avg_speed
        self.speed_sigma = speed_sigma

    def update(self):
        """
        Updatea and create/destroy cars
        """

        self.ticks += 1
        if FPS/self.ticks <= self.frequency:
            self.ticks = 0
            lane = random.choice(range(self.lanes)) * self.lanewidth
            v = np.random.normal(self.avg_speed, self.speed_sigma)
            newCar = Car(self.screen, self, (self.position[0], self.position[1] + lane), v)
            self.carlist.append(newCar)

        for car in self.carlist:
            car.updateLocal()

        for car in self.carlist:
            car.updateGlobal()
            if car.rect.left > width + 100:
                self.carlist.remove(car)
                del car
            else: car.draw()

if __name__ == "__main__":
    road = Road(screen, (0, height/2), lanewidth=5, frequency=2, lanes=2)

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(BLACK)
        road.update()

        print(road.carlist[1].speed if len(road.carlist) > 1 else "")

        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        clock.tick(FPS)
