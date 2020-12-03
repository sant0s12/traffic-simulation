import sys
import pygame
import json
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

def make_filename(f):
    fsplit = f.rsplit(".", 1)
    name = fsplit[0]
    ext = fsplit[1] if len(fsplit) > 1 else ""

    suff = ""
    i = 1
    while os.path.isfile(f'{name}{suff}.{ext}'): suff = i ; i += 1
    return f'{name}{suff}.{ext}'

def save_data(data, filename, overwrite=False):
    json.dump(data, open(make_filename(filename) if not overwrite else filename, "w"))

def read_data(filename):
    if not os.path.isfile(filename): return None
    else: return json.load(open(filename, "r"))

def dots_to_image(pixel_plot, filename, overwrite=False):
    from PIL import Image
    filename = (make_filename(filename) if not overwrite else filename)

    img = Image.fromarray(pixel_plot.astype('uint8') * 255, mode='L')
    img.save(filename)

if __name__ == "__main__":
    road_length = 50000
    a = Params(v_0=(30, 3), s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
    sim = Simulation(params_list=[a], delta_t=DELTA_T, car_frequency=1.5, road_length=road_length, road_lanes=1)

    filename = "testing.json"
    data = read_data(filename)
    if data is None:
        data = sim.run(1000)
        save_data(data, filename)

    dotgraph = Metrics.make_dots(data, road_length, time_div=5, delta_x=20)
    dots_to_image(dotgraph, "dot_image.png")
    # Metrics.show_dots(dotgraph)

"""    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        SCREEN.fill(BLACK)

        for car in datapoint:
            SCREEN.blit(car['surface'], car['rect'])

        pygame.display.update()
        CLOCK.tick(1./DELTA_T * SPEED) """
