import sys
import numpy as np
from tqdm import tqdm
from Road import Road

class Simulation:

    def __init__(self, params_list: list, road_position=(0, 0), road_length=1000, road_lanes=2, road_lane_width=5, car_frequency=1, delta_t=0.1):
        self.params_list = params_list
        self.delta_t = delta_t
        self.road = Road(params_list=params_list, position=road_position, lanewidth=road_lane_width, car_frequency=car_frequency, lanes=road_lanes, length=road_length)
        self.end = False

    def step(self):
        self.end |= self.road.update(delta_t=self.delta_t)
        return self.road.carlist

    def run(self, time=None):
        data = []
        if time is not None:
            for t in tqdm(np.arange(0, time, self.delta_t)):
                data.append([car.serialize() for car in self.step()])
        else:
            with tqdm(total=self.road.length) as pbar:
                lastpos = 0
                while not self.end:
                    first_car = None
                    cars_step = []
                    for car in self.step():
                        cars_step.append(car.serialize())
                        first_car = car if first_car is None or car.pos[0] > first_car.pos[0] else first_car
                    data.append(cars_step)
                    if first_car is not None:
                        pbar.update(int(first_car.pos[0]) - lastpos)
                        lastpos = int(first_car.pos[0])
        return data
