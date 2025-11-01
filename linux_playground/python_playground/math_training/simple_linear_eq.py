import numpy as np


def linear(x: float | np.float64, slope: int = 5, beginning: int = 0) -> float | np.float64:
    return x * slope + beginning


def quadratic(x: float | np.float64) -> float | np.float64:
    return x**2 - 4*x + 2

def slope_calc(x1, y1, x2, y2):
    """
    m = (y1-y2) / (x1-x2)
    """
    return abs(y1 - y2) / abs(x1 - x2)


if '__main__' == __name__:
    xs = np.linspace(0, 100)
    ys_linear = [linear(x) for x in xs]
    print(ys_linear)