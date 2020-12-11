import sys
import json
import os.path
import numpy as np
import matplotlib.pyplot as plt
from Simulation import Simulation
from DriverModel import Driver
from Metrics import Metrics
from Car import Params

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

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
    print("Saving data, this might take a while...")
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    json.dump(data, open(make_filename(filename) if not overwrite else filename, "w"))

def read_data(filename):
    if not os.path.isfile(filename): return None
    else:
        print("Loading data, this might take a while...")
        return json.load(open(filename, "r"))

def dots_to_image(pixel_plot, filename, mode='L', overwrite=False):
    from PIL import Image
    filename = (make_filename(filename) if not overwrite else filename)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img = Image.fromarray(pixel_plot.astype('uint8'), mode=mode)
    img.save(filename)

def dots_to_image_notSaved(pixel_plot):
    from PIL import Image

    return Image.fromarray(pixel_plot.astype('uint8'), mode='RGB')

def combine_and_Save(img1, img2, filename, overwrite = False):
    from PIL import Image
    filename = (make_filename(filename) if not overwrite else filename)
    img = Image.blend(img1, img2, 0.5)
    new_image = img.resize((int(img.width * 1),int(img.height *0.2) ), resample= Image.BILINEAR)
    new_image.save(filename)

def show_pygame(data, delta_t):
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
        CLOCK.tick(1./delta_t * SPEED)

if __name__ == "__main__":
    road_length = 50000
    delta_t = 0.3

    # With speed limit and constant params (standard)
    #===========================================================================================
    car_params = Params(T=1.4, a=2, b=2.5, delta=4, s_0=2, s_1=0, length=4.55,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=139829)

    trucc_params = Params(T=1.6, a=1, b=1.5, delta=4, s_0=2, s_1=0, length=16.5,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=7886)

    limits = [80, 100, 120, 140]
    fail_ps = [0, 1e-6, 1e-4, 1e-2]
    avg_table = np.zeros((len(fail_ps), len(limits)))

    folder='speedlimit/'
    filename_plot_groupped=folder + f'speedlimit_plot_groupped.svg'
    for i, p in enumerate(fail_ps):
        filename_plot=folder + f'speedlimit_plot_fail_{p}.svg'
        for j, l in enumerate(limits):
            filename_data=folder + f'speedlimit_{l}_fail_{p}.json'
            filename_average=folder + f'speedlimit_{l}_fail_{p}_average.json'
            filename_graph=folder + f'speedlimit_{l}_fail_{p}_graph.png'
            filename_average_plot=folder + f'speedlimit_{l}_fail_{p}_average_plot.svg'

            data = read_data(filename=filename_data)
            if data is None:
                print(f'Running simulation for speedlimit={l}, fail_p={p}')

                car_params.v_0 = (l/3.6, 5/3.6)
                car_params.fail_p = p

                trucc_params.v_0 = (min(l, 80)/3.6, 2.5/3.6)
                trucc_params.fail_p = p

                sim = Simulation([car_params, trucc_params], road_length=road_length, car_frequency=2, delta_t=delta_t)
                data = sim.run()
                save_data(data, filename_data, overwrite=True)

            avg = read_data(filename_average)
            if avg is None:
                avg = Metrics.avg_speed(data)
                save_data(avg, filename_average, overwrite=True)
            avg_table[i][j] = np.mean(avg)

            Metrics.plot_bins(100, avg, filename_average_plot)

            dots = Metrics.make_dots_bw(data, road_length, time_div=1, delta_x=10)
            dots_to_image(dots, filename_graph, overwrite=True)

        plt.bar(range(len(limits)), avg_table[i])
        plt.xticks(range(len(limits)), limits)
        plt.ylabel("Average speed")
        plt.xlabel("Speed limit")
        plt.savefig(filename_plot)
        plt.close()

    Metrics.plot_bar_groupped(avg_table, filename_plot_groupped, fail_ps, xticks=limits, ylabel="Average speed", xlabel="Speed limit")

    #===========================================================================================

    # With speed limit and constant params and a=0.3 for plotting
    #===========================================================================================
    car_params = Params(T=1.4, a=0.3, b=2.5, delta=4, s_0=2, s_1=0, length=4.55,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=139829)

    trucc_params = Params(T=1.6, a=0.3, b=1.5, delta=4, s_0=2, s_1=0, length=16.5,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=7886)

    limits = [80, 100, 120, 140]
    fail_ps = [0, 1e-6]
    avg_table = np.zeros((len(fail_ps), len(limits)))

    for i, p in enumerate(fail_ps):
        folder=f'speedlimit_a_0,3/{p}/'
        filename_plot_groupped=folder + f'speedlimit_plot_groupped_a_0,3.svg'
        filename_plot=folder + f'speedlimit_plot_fail_{p}_a_0,3.svg'
        for j, l in enumerate(limits):
            filename_data=folder + f'speedlimit_{l}_fail_{p}_a_0,3.json'
            filename_average=folder + f'speedlimit_{l}_fail_{p}_average_a_0,3.json'
            filename_graph=folder + f'speedlimit_{l}_fail_{p}_graph_a_0,3.png'
            filename_average_plot=folder + f'speedlimit_{l}_fail_{p}_average_plot_a_0,3.svg'

            data = read_data(filename=filename_data)
            if data is None:
                print(f'Running simulation for speedlimit={l}, fail_p={p}')

                car_params.v_0 = (l/3.6, 5/3.6)
                car_params.fail_p = p

                trucc_params.v_0 = (min(l, 80)/3.6, 2.5/3.6)
                trucc_params.fail_p = p

                sim = Simulation([car_params, trucc_params], road_length=road_length, car_frequency=2, delta_t=delta_t)
                data = sim.run()
                save_data(data, filename_data, overwrite=True)

            avg = read_data(filename_average)
            if avg is None:
                avg = Metrics.avg_speed(data)
                save_data(avg, filename_average, overwrite=True)
            avg_table[i][j] = np.mean(avg)

            Metrics.plot_bins(100, avg, filename_average_plot)

            dots = Metrics.make_dots_bw(data, road_length, time_div=1, delta_x=10)
            dots_to_image(dots, filename_graph, overwrite=True)

        plt.bar(range(len(limits)), avg_table[i])
        plt.xticks(range(len(limits)), limits)
        plt.ylabel("Average speed")
        plt.xlabel("Speed limit")
        plt.savefig(filename_plot)
        plt.close()

    Metrics.plot_bar_groupped(avg_table, filename_plot_groupped, fail_ps, xticks=limits, ylabel="Average speed", xlabel="Speed limit")

    #===========================================================================================


    # With no speed limit and constant params
    #===========================================================================================
    car_params = Params(T=1.4, a=2, b=2.5, delta=4, s_0=2, s_1=0, length=4.55,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=139829)

    trucc_params = Params(T=1.6, a=1, b=1.5, delta=4, s_0=2, s_1=0, length=16.5,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=7886)

    avgs = [100, 120, 140, 160, 180]
    widths = [10, 15, 20]
    fail_ps = [0, 1e-6]
    avg_table = np.zeros((len(widths), len(avgs)))

    for p in fail_ps:
        folder=f'no_speedlimit/{p}/'
        filename_plot_groupped=folder + f'no_speedlimit_graph_groupped.svg'
        for i, w in enumerate(widths):
            filename_plot=folder + f'no_speedlimit_plot_width_{w}.svg'
            for j, a in enumerate(avgs):
                filename_data=folder + f'no_speedlimit_({a}, {w})_fail_{p}.json'
                filename_average=folder + f'no_speedlimit_({a}, {w})_fail_{p}_average.json'
                filename_graph=folder + f'no_speedlimit_({a}, {w})_fail_{p}.png'
                filename_average_plot=folder + f'no_speedlimit_{a}_width_{w}_average_plot.svg'

                data = read_data(filename=filename_data)
                if data is None:
                    print(f'Running simulation for average speed={a}, width={w}, fail_p={p}')

                    car_params.v_0 = (a/3.6, w/3.6)
                    car_params.fail_p = p

                    trucc_params.v_0 = (min(a, 80)/3.6, 2.5/3.6)
                    trucc_params.fail_p = p

                    sim = Simulation([car_params, trucc_params], road_length=road_length, car_frequency=2, delta_t=delta_t)
                    data = sim.run()
                    save_data(data, filename_data, overwrite=True)

                avg = read_data(filename_average)
                if avg is None:
                    avg = Metrics.avg_speed(data)
                    save_data(avg, filename_average, overwrite=True)
                avg_table[i][j] = np.mean(avg)

                Metrics.plot_bins(100, avg, filename_average_plot)

                dots = Metrics.make_dots_bw(data, road_length, time_div=1, delta_x=10)
                dots_to_image(dots, filename_graph, overwrite=True)

            plt.bar(range(len(avgs)), avg_table[i])
            plt.xticks(range(len(avgs)), avgs)
            plt.ylabel("Average speed")
            plt.xlabel("Average desired speed")
            plt.savefig(filename_plot)
            plt.close()

        Metrics.plot_bar_groupped(avg_table, filename_plot_groupped, widths, xticks=avgs, ylabel="Average speed", xlabel="Desired speed")
    #===========================================================================================

    # With no speed limit and a=0.3
    #===========================================================================================
    car_params = Params(T=1.4, a=0.3, b=2.5, delta=4, s_0=2, s_1=0, length=4.55,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=139829)

    trucc_params = Params(T=1.6, a=0.3, b=1.5, delta=4, s_0=2, s_1=0, length=16.5,
                        thr=0.3, pol=0.25, right_bias=0.3, fail_steps=900,
                        spawn_weight=7886)

    avgs = [100, 120, 140, 160, 180]
    widths = [10, 15, 20]
    fail_ps = [0, 1e-06]
    avg_table = np.zeros((len(widths), len(avgs)))

    for p in fail_ps:
        folder=f'no_speedlimit_a_0,3/{p}/'
        filename_plot_groupped=folder + f'no_speedlimit_graph_groupped_a_0,3.svg'
        for i, w in enumerate(widths):
            filename_plot=folder + f'no_speedlimit_plot_width_{w}_a_0,3.svg'
            for j, a in enumerate(avgs):
                filename_data=folder + f'no_speedlimit_({a}, {w})_fail_{p}_a_0,3.json'
                filename_average=folder + f'no_speedlimit_({a}, {w})_fail_{p}_average_a_0,3.json'
                filename_graph=folder + f'no_speedlimit_({a}, {w})_fail_{p}_a_0,3.png'
                filename_average_plot=folder + f'no_speedlimit_{a}_width_{w}_average_plot_a_0,3.svg'

                data = read_data(filename=filename_data)
                if data is None:
                    print(f'Running simulation for average speed={a}, width={w}, fail_p={p}')

                    car_params.v_0 = (a/3.6, w/3.6)
                    car_params.fail_p = p

                    trucc_params.v_0 = (min(a, 80)/3.6, 2.5/3.6)
                    trucc_params.fail_p = p

                    sim = Simulation([car_params, trucc_params], road_length=road_length, car_frequency=2, delta_t=delta_t)
                    data = sim.run()
                    save_data(data, filename_data, overwrite=True)

                avg = read_data(filename_average)
                if avg is None:
                    avg = Metrics.avg_speed(data)
                    save_data(avg, filename_average, overwrite=True)
                avg_table[i][j] = np.mean(avg)

                Metrics.plot_bins(100, avg, filename_average_plot)

                dots = Metrics.make_dots_bw(data, road_length, time_div=1, delta_x=10)
                dots_to_image(dots, filename_graph, overwrite=True)

            plt.bar(range(len(avgs)), avg_table[i])
            plt.xticks(range(len(avgs)), avgs)
            plt.ylabel("Average speed")
            plt.xlabel("Average desired speed")
            plt.savefig(filename_plot)
            plt.close()

        Metrics.plot_bar_groupped(avg_table, filename_plot_groupped, widths, xticks=avgs, ylabel="Average speed", xlabel="Desired speed")
    #===========================================================================================
