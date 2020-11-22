from Simulation import Simulation
from DriverModel import Driver, ModelParams
FPS = 100 # FPS will be capped to 1/STEP
STEP = 0.1 # delta_t in seconds

#SIZE = WIDTH, HEIGHT = 1000, 100
#SCREEN = pygame.display.set_mode(SIZE)

def dist(a, b):
    return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

if __name__ == "__main__":
    a = ModelParams(v_0=120, s_0=2, s_1=0, T=1.6, a=2, b=1.67, delta=4, length=5, thr=0.4, pol=0.5)
    sim = Simulation([a], 0.01)
    print(sim.run(5))

    """pygame.init()


    road = Road(SCREEN, (0, HEIGHT/2), lanewidth=5, frequency=1, lanes=3, avg_speed=30, speed_sigma=1)

    debugCar = None

    # Main game loop
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for car in road.carlist:
                    if debugCar is None or dist(car.pos, mouse_pos) < dist(debugCar.pos, mouse_pos):
                        debugCar = car
            if event.type == pygame.KEYDOWN and debugCar is not None:
                if event.key == pygame.K_UP: debugCar.driver.modelParams.v_0 += 10 / 3.6
                if event.key == pygame.K_DOWN: debugCar.driver.modelParams.v_0 = max(debugCar.driver.modelParams.v_0 - 10/3.6, np.finfo(float).eps)

        SCREEN.fill(BLACK)
        road.update()

        if debugCar is not None:

            for car in debugCar.getCarsAround().values():
                if car is None: continue
                car.surface.fill((0,0,255))
                car.draw()
                car.surface.fill(WHITE)

            # debugCar.v = 0
            debugCar.surface.fill((255,0,0))
            debugCar.draw()
            debugCar.surface.fill(WHITE)

            print("{} kmh out of {} kmh".format(debugCar.v * 3.6, debugCar.driver.modelParams.v_0 * 3.6))

        # Refresh the screen and tick the clock (for 60 fps)
        pygame.display.update()
        CLOCK.tick(FPS) """
