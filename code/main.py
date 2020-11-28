import sys
import pygame
import math
from Simulation import Simulation
from DriverModel import Driver, ModelParams

BLACK = (0, 65, 0)
WHITE = (255, 255, 255)
SHOWSPEED = False

DELTA_T = 0.1 # delta_t in seconds
SPEED = 5 # playback speed of the data (1 for real time)

LANE_AMT = 1
SIZE = WIDTH, HEIGHT = 1000, 40+(20*LANE_AMT)
SCREEN = pygame.display.set_mode(SIZE)
TOPLANE = pygame.image.load("toplane.png")
MIDDLELANE = pygame.image.load("middlelane.png")
BOTTOMLANE = pygame.image.load("bottomlane.png")
pygame.font.init()
FONT = pygame.font.SysFont('Comic Sans MS', 30)

CLOCK = pygame.time.Clock()

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

if __name__ == "__main__":
    a = ModelParams(v_0=300, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=10, thr=0.4, pol=0)
    sim = Simulation(modelParamsList=[a], roadPosition=(0,30), lanewideness = 20, delta_t=DELTA_T, lanes_amt=LANE_AMT, car_frequency=1)
    data = sim.run(50)
    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    SPEED = max(1, SPEED-30)
                    SHOWSPEED = True
                if event.key == pygame.K_RIGHT:
                    SPEED = SPEED+30
                    SHOWSPEED = True

        SCREEN.fill(BLACK)
        SCREEN.blit(TOPLANE, (0,20))
        for i in range(1, (LANE_AMT-1)):
            SCREEN.blit(MIDDLELANE, (0,20*(i+1)))
        SCREEN.blit(BOTTOMLANE, (0,20*LANE_AMT))

        if SHOWSPEED: SCREEN.blit(FONT.render("Speed: " + str(SPEED), True, WHITE), (10,10))



        avg_sum = 0.
        for car in datapoint:
            SCREEN.blit(car['surface'], car['rect'])
            avg_sum += car['v'] * 3.6
        print(avg_sum/len(datapoint))

        pygame.display.update()
        CLOCK.tick(1./DELTA_T * SPEED)
