

from linux_playground.python_playground.math_training.plot_view import PlotView
from linux_playground.python_playground.math_training.simple_linear_eq import linear, quadratic
from linux_playground.python_playground.math_training.wp_creator import WpGenerator, WpGeneratorSlope


wp_linear = WpGenerator(name="linear", x_axis_count=100, 
                        generate_y_axis_callback=linear)

wp_quadratic = WpGenerator(name="quadratic", x_axis_count=100,
                         generate_y_axis_callback=quadratic)

wp_linear_slope = WpGeneratorSlope(name="lol2", x1=1, x2=100, y1=3, y2=9)

pv = PlotView()
pv.add_wp(wp_generator=wp_linear)
pv.add_wp(wp_generator=wp_quadratic)
pv.add_wp(wp_generator=wp_linear_slope)
pv.show()