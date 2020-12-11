import sys
import numpy as np
from tqdm import tqdm
from Road import Road
from collections import deque

class Simulation:
    """Class to manage the simulation

    Args:
        params_list: List of car params defining the different car types
        road_position: Position of the top most lane
        road_length: Road length
        road_lanes: Amount of lanes
        road_lane_width: Width of the car lanes
        delta_t: Time step to use when running the simulation
    """

    def __init__(self, params_list: list, road_position=(0, 0), road_length=1000, road_lanes=2, road_lane_width=5, car_frequency=1, delta_t=0.1):
        self.params_list = params_list
        self.delta_t = delta_t
        self.road = Road(params_list=params_list, position=road_position, lanewidth=road_lane_width, car_frequency=car_frequency, lanes=road_lanes, length=road_length)
        self.end = False # Flag to end the simulation

    def step(self):
        """Run just one step of the simulation

        Returns: True if a car has reached the end of the simulation
        """

        self.end |= self.road.update(delta_t=self.delta_t)
        return self.road.carlist

    def run(self, time=None):
        """Run the simulation either for `time` seconds or until a car reaches the end of the road
        
        Args:
            optional time: Amount of time (in seconds) to run the simulation
        """

        data = deque()
        if time is not None:
            # This runs the simulation for time seconds
            for t in tqdm(np.arange(0, time, self.delta_t)):
                data.append([car.serialize() for car in self.step()])
        else:
            # This runs the simulation until a car reaches the end
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
                        pbar.set_description("#cars: " + str(len(self.road.carlist)))
                        pbar.update(max(int(first_car.pos[0]) - lastpos, 0))
                        lastpos = int(first_car.pos[0])
        return list(data)
