import sys
import json
import os.path
from Simulation import Simulation
from DriverModel import Driver
from Metrics import Metrics
from Car import Params

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

DELTA_T = 0.1 # delta_t in seconds

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
    else:
        print("Loading data, this might take a while...")
        return json.load(open(filename, "r"))

def dots_to_image(pixel_plot, filename, overwrite=False):
    from PIL import Image
    filename = (make_filename(filename) if not overwrite else filename)

    img = Image.fromarray(pixel_plot.astype('uint8'), mode='RGB')
    img.save(filename)

def show_pygame(data):
    import pygame
    SPEED = 5 # playback speed of the data (1 for real time)

    SIZE = WIDTH, HEIGHT = 1000, 100
    SCREEN = pygame.display.set_mode(SIZE)

    CLOCK = pygame.time.Clock()

    pygame.init()

    for datapoint in data:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP: SPEED += 1
                if event.key == pygame.K_DOWN: SPEED = max(1, SPEED - 1)

        SCREEN.fill(BLACK)

        for car in datapoint:
            car_surface = pygame.Surface((car['length'], 2))
            car_surface.fill(WHITE)
            car_rect = car_surface.get_rect()
            car_rect.center = car['pos']
            SCREEN.blit(car_surface, car_rect)

        pygame.display.update()
        CLOCK.tick(1./DELTA_T * SPEED)

if __name__ == "__main__":
    road_length = 50000
    a = Params(v_0=(25, 0), s_0=2, s_1=0, T=2, a=0.85, b=3, delta=4, length=5, thr=0.4, pol=0.5, spawn_weight=1000, right_bias=0.41, fail_p=0.000001, fail_steps = 2000)
    b = Params(v_0=10, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=10, thr=0.4, pol=0.5, spawn_weight=20, right_bias=0.41)
    sim = Simulation(params_list=[a], delta_t=DELTA_T, car_frequency=1.8, road_length=road_length, road_lanes=2)

    filename = "zibung.json"
    data = read_data(filename)
    if data is None:
        data = sim.run()
        save_data(data, filename)


    dotgraph = Metrics.make_dots(data, road_length, time_div=1, delta_x=10)
    dots_to_image(dotgraph, "dot_image.png")
