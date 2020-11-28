import numpy as np

class Metrics:
    """Class with functions to get all the different metrics we need
    """

    def __roundClosest(a, b):
        return b * round(a/b)

    def avgSpeed(carData: list, dela_t: float):
        avgList = []
        for data_t in carData:
            speedArray = np.array([car['v'] * 3.6 for car in data_t])
            avgList.append(np.average(speedArray))
        return avgList

    def medianSpeed(carData: list, delta_t: float):
        medianList = []
        for data_t in carData:
            speedArray = np.median([car['v'] * 3.6 for car in data_t])
            medianList.append(np.average(speedArray))
        return medianList

    def plotDots(carData: list, roadLength: int, time_div: float, delta_x: float):
        pixelPlot = np.zeros((len(carData[::time_div]), round(roadLength/delta_x)))
        print(pixelPlot.shape)
        for i, data_t in enumerate(carData[::time_div]):
            for car in data_t:
                x = int(np.floor(car['pos'][0]/delta_x))
                if car['pos'][1] != 0 or x >= pixelPlot.shape[1]:  continue
                pixelPlot[i][x] = 1
        return pixelPlot
