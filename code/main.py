import sys
import pygame
import random
import numpy as np
from driverModel import Driver
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

size = width, height = 1000, 1000
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
        self.surface = pygame.Surface((10, 10))
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()

        self.pos = list(startpos)
        self.rect.center = startpos

        self.screen = screen
        self.road: 'Road' = road
        self.speed = 10

        self.model = Driver(0, 50, 1.6, 0.73, 1.67, 4, 2, 0, 10) # To be tweaked

    def update(self):
        """
        Move object along direction vector
        """

        carInFront = None
        for car in self.road.carlist:
            if car.pos[0] > self.pos[0]:
                carInFront = car if (carInFront is None or car.pos[0] < carInFront.pos[0]) else carInFront
            else: continue

        accel = self.model.getAccel((carInFront.pos[0] - self.pos[0]) if carInFront is not None else 100000, 
                                    carInFront.speed if carInFront is not None else self.speed)
        self.speed += accel
        self.speed = max(self.speed, 0)

        self.pos[0] += self.speed/100
        self.rect.center = self.pos # hself.direction)

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

    def __init__(self, screen, position, lanes=2, lanewidth=5, frequency=60, avg_speed=100, speed_sigma=10):
        self.screen = screen
        self.carlist: list[Car] = []
        self.frequency = frequency
        self.ticks = frequency
        self.position = position
        self.lanes = lanes
        self.lanewidth = lanewidth
        self.avg_speed = avg_speed
        self.speed_sigma = speed_sigma

    def update(self):
        """
        Updatea and create/destroy cars
        """

        self.ticks += 1
        if self.ticks >= self.frequency:
            self.ticks = 0
            lane = random.choice(range(self.lanes)) * self.lanewidth
            v = np.random.normal(self.avg_speed, self.speed_sigma)
            newCar = Car(self.screen, self, (self.position[0], self.position[1] + lane), v)
            self.carlist.append(newCar)

        for car in self.carlist:
            if car.rect.left > width:
                self.carlist.remove(car)
                del car
            else:
                car.update()
                car.draw()

if __name__ == "__main__":
    road = Road(screen, (0, height/2), lanewidth=20, frequency=50, lanes=1)

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(BLACK)
        road.update()

        print(road.carlist[0].speed)


        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        clock.tick(60)
