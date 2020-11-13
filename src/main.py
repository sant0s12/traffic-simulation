import sys
import pygame
pygame.init()

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

size = width, height = 1000, 1000
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

class Car(pygame.sprite.Sprite):
    def __init__(self, screen, startpos, direction):
        super(Car, self).__init__()
        self.surface = pygame.Surface((10, 10))
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()
        self.rect.center = startpos
        self.screen = screen
        self.direction = direction

    def update(self):
        self.rect.move_ip(self.direction)

    def draw(self):
        screen.blit(self.surface, self.rect)

class CarMaker:
    def __init__(self, screen, frequency=60):
        self.screen = screen
        self.carlist = []
        self.frequency = 60
        self.ticks = 0

    def update(self):
        self.ticks += 1
        if self.ticks == self.frequency:
            self.ticks = 0
            newCar = Car(self.screen, (0, height/2), (1,0))
            self.carlist.append(newCar)

        for car in self.carlist:
            if car.rect.left > width:
                self.carlist.remove(car)
                del car
            else:
                car.update()
                car.draw()

if __name__ == "__main__":
    carMaker = CarMaker(screen)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(BLACK)
        carMaker.update()

        pygame.display.update()
        clock.tick(60)
