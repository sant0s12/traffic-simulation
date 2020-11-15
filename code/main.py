import sys
import pygame
import random
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
    def __init__(self, screen, road, startpos, direction):
        super(Car, self).__init__()
        self.surface = pygame.Surface((10, 10))
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()
        self.rect.center = startpos
        self.screen = screen
        self.road = road
        self.direction = direction

    def update(self):
        """
        Move object along direction vector
        """

        self.rect.move_ip(self.direction)

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

    def __init__(self, screen, position, lanes=2, lanewidth=5, frequency=60):
        self.screen = screen
        self.carlist = []
        self.frequency = frequency
        self.ticks = frequency
        self.position = position
        self.lanes = lanes
        self.lanewidth = lanewidth

    def update(self):
        """
        Updatea and create/destroy cars
        """

        self.ticks += 1
        if self.ticks >= self.frequency:
            self.ticks = 0
            lane = random.choice(range(self.lanes)) * self.lanewidth
            newCar = Car(self.screen, self, (self.position[0], self.position[1] + lane), (1,0))
            self.carlist.append(newCar)

        for car in self.carlist:
            if car.rect.left > width:
                self.carlist.remove(car)
                del car
            else:
                car.update()
                car.draw()

if __name__ == "__main__":
    road = Road(screen, (0, height/2), lanewidth=20, frequency=30, lanes=5)

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(BLACK)
        road.update()

        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        clock.tick(60)
