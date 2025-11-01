from abc import ABC
from typing import Callable, Optional

import numpy as np

from linux_playground.python_playground.math_training.simple_linear_eq import linear, slope_calc

import plotly.express as px

import pandas as pd

class Wp(ABC):
    def __init__(self, name: str):
        self.name = name
        self.x_axis_generated: Optional[np.ndarray[np.float64]]
        self.y_axis_generated: Optional[np.ndarray[np.float64] | list[float]]

class WpGenerator(Wp):
    def __init__(self, name: str, x_axis_count: int, generate_y_axis_callback: Callable):
        """
        y_axis generates thorugh the x_axis count and the callable functionallity of the 
        Working Point Generator.
        """
        super().__init__(name)
        self.x_axis_count: int = x_axis_count
        self.x_axis_generated: np.ndarray[np.float64] = np.linspace(0, self.x_axis_count)
        self.generate_y_axis_callback: Callable = generate_y_axis_callback
        self.y_axis_generated = self.__y_axis_generator()

    def __y_axis_generator(self) -> list[float]:
        return [self.generate_y_axis_callback(x) for x in self.x_axis_generated]
    
    def df_generator(self):
        return pd.DataFrame({
            "x": self.x_axis_generated,
            "y": self.y_axis_generated
        })

    def __str__(self):
        return f"x_axis: {self.x_axis_generated}, y_axis: {self.y_axis_generated}"


class WpGeneratorSlope(Wp):
    def __init__(self, name: str, x1, x2, y1, y2):
        super().__init__(name)
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.m: Optional[float] = None
        self.wp: Optional[list[tuple[float]]] = self.generate_wp_from_slope()

    
    def generate_wp_from_slope(self, num_points: int = 50):
        # step 1 calc slope
        self.m = slope_calc(self.x1, self.y1, self.x2, self.y2)

        # step 2 calc wp from slop
        x_points = np.linspace(self.x1, self.x2, num_points)
        y_points = self.y1 + self.m * (x_points - self.x1)

        self.wp = list(zip(x_points, y_points))
        self.x_axis_generated = x_points
        self.y_axis_generated = y_points
        return self.wp
