import random
import Car

class Road:
    """Road object to keep track of all the cars, create and destroy them when they are outside the simulation bounds

    Args:
        position: position of the the top most lane
        lanes: amount of lanes
        lanewidth: width of the lanes
        car_frequency: car creation frequency
        length: road lenght
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
        lane = random.choice(range(self.lanes)) * self.lanewidth

        distribution = [m.spawn_weight for m in self.params_list]
        models = [m for m in self.params_list]
        params = random.choices(models, weights=distribution, k=1)[0]
        new_car = Car.Car(params=params.apply_dist(), road=self, startpos=[self.position[0], self.position[1] + lane])

        car_front = new_car.get_cars_around()["frontNow"]

        if car_front is not None:
            t = (car_front.pos_back - new_car.pos_front) / new_car.v if new_car.v != 0 else new_car.params.T
            clipping = (car_front.pos_back - new_car.pos_front) <= 0
        else:
            t = new_car.params.T
            clipping = False

        if t >= new_car.params.T and not clipping:
            self.carlist.append(new_car)
            return True
        else:
            return False

    def update(self, delta_t: float):
        """Create cars and update all the cars in the list
        """
        car_reached_end = False

        for car in self.carlist:
            car.update_local(delta_t)

        for car in self.carlist:
            car.update_global()
            if car.rect.left > self.length:
                self.carlist.remove(car)
                car_reached_end = True

        self.last_new_car_t += delta_t
        if self.last_new_car_t >= 1.0/self.car_frequency and self.spawn_car():
            self.last_new_car_t = 0

        return car_reached_end

    def draw(self, screen):
        for car in self.carlist:
            car.draw(screen)
