import sys
import pygame
import matplotlib.pyplot as plt
import pickle
import os.path
from Simulation import Simulation
from DriverModel import Driver
from Metrics import Metrics
from Car import Params

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DELTA_T = 0.1 # delta_t in seconds
SPEED = 5 # playback speed of the data (1 for real time)

SIZE = WIDTH, HEIGHT = 1000, 100
#SCREEN = pygame.display.set_mode(SIZE)

CLOCK = pygame.time.Clock()

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def save_data(data, filename, overwrite=False):
    def make_filename(f):
        suff = ""
        i = 1
        while os.path.isfile(f'{f}{suff}'): suff = i ; i += 1
        return f'{f}{suff}'

    pickle.dump(data, open(make_filename(filename), "wb"))

def read_data(filename):
    if not os.path.isfile(filename): return None
    else: return picke.load(open(filename, "rb"))

if __name__ == "__main__":
    road_length = 5000
    a = Params(v_0=30, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
    sim = Simulation(params_list=[a], delta_t=DELTA_T, car_frequency=1.5, road_length=road_length)
    data = sim.run(50)
    save_data(data, "agsh")

    imdata = Metrics.plot_dots(data, road_length, 1, 5)
    plt.imshow(imdata, cmap='gray')
    plt.show()

"""    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        SCREEN.fill(BLACK)

        for car in datapoint:
            SCREEN.blit(car['surface'], car['rect'])

        pygame.display.update()
        CLOCK.tick(1./DELTA_T * SPEED) """
