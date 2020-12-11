
import numpy as np

import random

import Car

class Road:
    """Road class to keep track of all the cars, create and destroy them when they are outside the simulation bounds

    Args:
        params_list: List of car params defining the different car types
        position: Position of the top most lane
        lanes: Amount of lanes
        lanewidth: Width of the lanes
        car_frequency: Car creation frequency
        length: Road length
    """

    def __init__(self, params_list, position, lanes, lanewidth, length, car_frequency):
        self.params_list = params_list
        self.car_frequency = car_frequency
        self.last_new_car_t = 1.0/car_frequency # Time since last car creation

        self.position = position
        self.length = length
        self.lanes = lanes
        self.lanewidth = lanewidth
        self.toplane = self.position[1] # Position of top lane
        self.bottomlane = self.toplane + lanewidth * (lanes - 1)

        self.carlist: list[Car.Car] = [] # List of cars on the load

    def spawn_car(self):
        """Create new car with the given frequency only if there is enough distance to the next car

        Returns: True if a car could be spawned, False otherwise
        """

        # Select random lane
        lane = int(np.random.choice(range(self.lanes)) * self.lanewidth)

        # Choose car type randomly based on the weight
        distribution = np.array([m.spawn_weight for m in self.params_list])
        models = [m for m in self.params_list]
        params = np.random.choice(models, p=(distribution/distribution.sum()))

        # Create new car
        new_car = Car.Car(params=params.apply_dist(), road=self, startpos=[self.position[0], self.position[1] + lane])

        # Look for the car that would be in front when this car spawned
        car_front = new_car.get_cars_around()["frontNow"]

        if car_front is not None:
            t = (car_front.pos_back - new_car.pos_front) / new_car.v if new_car.v != 0 else new_car.params.T
            clipping = (car_front.pos_back - new_car.pos_front) <= 0
        else:
            t = new_car.params.T+2
            clipping = False

        # If it is safe to spawn the car, then do so
        if t >= new_car.params.T +2 and not clipping:
            self.carlist.append(new_car)
            return True
        else:
            return False

    def update(self, delta_t: float):
        """Create cars and update all the cars in the list
        Args:
            delta_t: Time step to simulate

        Returns: True if a car reached the end of the road during this step
        """

        car_reached_end = False

        # Update the local state of all the cars
        for car in self.carlist:
            car.update_local(delta_t)

        # Update the global state of all the cars
        for car in self.carlist:
            car.update_global()

            # If a car is outside the road, then delete it from the list and set the return flag
            if car.pos_back > self.length:
                self.carlist.remove(car)
                car_reached_end = True

        # Try to spawn a car if the time has come
        self.last_new_car_t += delta_t
        if self.last_new_car_t >= 1.0/self.car_frequency and self.spawn_car():
            self.last_new_car_t = 0

        return car_reached_end
