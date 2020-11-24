import sys
import pygame
from Simulation import Simulation
from DriverModel import Driver, ModelParams

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

STEP = 0.1 # delta_t in seconds
SPEED = 10 # playback speed of the data (1 for real time)

SIZE = WIDTH, HEIGHT = 1000, 100
SCREEN = pygame.display.set_mode(SIZE)

CLOCK = pygame.time.Clock()

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

if __name__ == "__main__":
    a = ModelParams(v_0=120, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
    sim = Simulation([a], 0.01)
    data = sim.run(50)

    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        SCREEN.fill(BLACK)

        for car in datapoint:
            SCREEN.blit(car['surface'], car['rect'])

        pygame.display.update()
        CLOCK.tick(1./STEP * SPEED)
