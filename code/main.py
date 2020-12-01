import sys
import pygame
from Simulation import Simulation
from DriverModel import Driver, ModelParams

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DELTA_T = 0.1 # delta_t in seconds
SPEED = 5 # playback speed of the data (1 for real time)

SIZE = WIDTH, HEIGHT = 1000, 100
SCREEN = pygame.display.set_mode(SIZE)

CLOCK = pygame.time.Clock()

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

if __name__ == "__main__":
    a = ModelParams(v_0=30, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5, fs=5, fp=0.01)
	# v_0 = 125 and 80 km/h, rest are standard values from the paper/traffic-simulation.de
    car_normal = ModelParams(v_0=34.72, T=1.5, a=0.3, b=3, delta=4, s_0=2, s_1=0, length=5, thr=0.2, pol=0.5)
    truck_normal = ModelParams(v_0=22.224, T=1.7, a=0.3, b=2, delta=4, s_0=2, s_1=0, length=16.5, thr=0.2, pol=0.5)

    sim = Simulation(model_params_list=[(car_normal, 126090), (truck_normal, 6730)], delta_t=DELTA_T, car_frequency=1/1.6)
    data = sim.run(250)

    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        SCREEN.fill(BLACK)

        avg_sum = 0.
        for car in datapoint:
            SCREEN.blit(car['surface'], car['rect'])
            avg_sum += car['v'] * 3.6
        print(avg_sum/len(datapoint))

        pygame.display.update()
        CLOCK.tick(1./DELTA_T * SPEED)
