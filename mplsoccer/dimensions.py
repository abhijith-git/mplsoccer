""" mplsoccer pitch dimensions.

Note that for tracab, uefa, metricasports, custom, and skillcorner the dimensions are in meters
(or centimeters for tracab). Real-life pictures are in actually measured in yards and the meter conversions
for distances (e.g. penalty_area_length) are slightly different, but for the purposes of the visualisations
the differences will be minimal.

Wycout dimensions are sourced from ggsoccer https://github.com/Torvaney/ggsoccer/blob/master/R/dimensions.R
Note, the goal width in ggsoccer (12 units) is different from socceraction (10 units)
(https://github.com/ML-KULeuven/socceraction/blob/master/socceraction/spadl/wyscout.py),
I am not sure which is correct, but I have gone for the goal width from ggsoccer (12 units).
In the previous versions of mplsoccer (up to 0.0.21), I used the socceraction goal width (10 units).
I changed it because it matters now for converting coordinates to a common dimension and wanted
to be consistent with ggsoccer.

Map of the pitch dimensions:


(left, top)     _______________________________________________________________   (right, top)
               |                               |                               |       ^                          
               |                               |                               |       |
               |----------                     |                     ----------|       |              ^
               |         |                     |                     |         |       |              |
               |----     |                     |                     |     ----|       |      ^       |
               |    |    |     (center_length, center_width)         |     |   |       |      |       | 
      ^    ~~~~|    |    |                     |                     |     |   |~~~~   |width |six_   | penalty_     
goal  |    |xxx|    | °  |penalty_left         °       penalty_right | °   |   |xxx|   |      |yard_  | area_
width |    |xxx|    |    |                     |                     |     |   |xxx|   |      |width  | width
      v    ~~~~|    |    |                     |                     |     |   |~~~~   |      |       |
               |____|    |                     |                     |     |___|       |      v       |
               |         |                     |                     |         |       |              |
               |---------                      |                     ----------|       |              v
               |                               |                               |       |
               | ______________________________|_______________________________|       v
(left, bottom)                                                                   (right, bottom)
                <-------------------------------------------------------------->
                                             length
                                        <-------------->
                                        circle_diameter
               <--->
           six_yard_length
           <--><--------->
    goal_length penalty_area_length

Other dimensions:

aspect = This is used to stretch a square dimension pitch (e.g. 1x1 or 100x100) to a rectangular pitch shape.
         For wyscout and opta pitches. I use 68/105. For metricasports, it is
         calculated via the specified pitch_length divided by the pitch_width.
invert_y = If true, the origin starts at (left, top)
origin_center = If true, the origin starts at (center length, center width)
"""

from dataclasses import dataclass, InitVar
from typing import Optional

import numpy as np

valid = ['statsbomb', 'tracab', 'opta', 'wyscout', 'uefa',
         'metricasports', 'custom', 'skillcorner', 'secondspectrum']
size_varies = ['tracab', 'metricasports', 'custom', 'skillcorner', 'secondspectrum']


@dataclass
class BaseDims:
    pitch_width: float
    pitch_length: float
    goal_width: float
    goal_length: float
    six_yard_width: float
    six_yard_length: float
    penalty_area_width: float
    penalty_area_length: float
    circle_diameter: float
    arc: Optional[float]
    invert_y: bool
    origin_center: bool
    # dimensions that can be calculated in __post_init__
    left: Optional[float] = None
    right: Optional[float] = None
    bottom: Optional[float] = None
    top: Optional[float] = None
    aspect: Optional[float] = None
    width: Optional[float] = None
    length: Optional[float] = None
    goal_bottom: Optional[float] = None
    goal_top: Optional[float] = None
    six_yard_left: Optional[float] = None
    six_yard_right: Optional[float] = None
    six_yard_bottom: Optional[float] = None
    six_yard_top: Optional[float] = None
    penalty_left: Optional[float] = None
    penalty_right: Optional[float] = None
    penalty_area_left: Optional[float] = None
    penalty_area_right: Optional[float] = None
    penalty_area_bottom: Optional[float] = None
    penalty_area_top: Optional[float] = None
    center_width: Optional[float] = None
    center_length: Optional[float] = None
    # defined in pitch_markings
    x_markings: Optional[np.array] = None
    y_markings: Optional[np.array] = None
    # defined in juego_de_posicion
    positional_x: Optional[np.array] = None
    positional_y: Optional[np.array] = None
    # defined in stripes
    stripe_locations: Optional[np.array] = None

    def setup_dims(self):
        self.pitch_markings()
        self.juego_de_posicion()
        self.stripes()

    def pitch_markings(self):
        self.x_markings = np.array([self.left, self.six_yard_left, self.penalty_left, self.penalty_area_left,
                                    self.center_length,
                                    self.penalty_area_right, self.penalty_right, self.six_yard_right, self.right])

        self.y_markings = np.array([self.bottom, self.penalty_area_bottom,
                                    self.six_yard_bottom, self.goal_bottom, self.goal_top, self.six_yard_top,
                                    self.penalty_area_top, self.top])
        if self.invert_y:
            self.y_markings = np.sort(self.y_markings)

    def juego_de_posicion(self):
        self.positional_x = np.array([self.left, self.penalty_area_left,
                                      self.penalty_area_left + (self.center_length - self.penalty_area_left) / 2.,
                                      self.center_length,
                                      self.center_length + (self.penalty_area_right - self.center_length) / 2.,
                                      self.penalty_area_right, self.right])
        self.positional_y = self.y_markings[[0, 1, 2, 5, 6, 7]]  # remove goal posts from pitch_markings

    def stripes(self):
        stripe_pen_area = (self.penalty_area_length - self.six_yard_length) / 2.
        stripe_other = (self.length - 2 * self.six_yard_length - 6 * stripe_pen_area) / 10.
        stripe_locations = ([self.left] + [self.six_yard_length] + [stripe_pen_area] * 3 +
                            [stripe_other] * 10 + [stripe_pen_area] * 3 + [self.six_yard_length])
        self.stripe_locations = np.array(stripe_locations).cumsum()

    def penalty_box_dims(self):
        self.penalty_right = self.right - self.penalty_left
        self.penalty_area_left = self.penalty_area_length
        self.penalty_area_right = self.right - self.penalty_area_length
        # if inverted then need to go in the other direction for the bottom
        if self.invert_y: 
            neg_if_inverted = - 1
        else:
            neg_if_inverted = 1
        self.penalty_area_bottom = self.center_width - (neg_if_inverted * self.penalty_area_width / 2)
        self.penalty_area_top = self.center_width + (neg_if_inverted * self.penalty_area_width / 2)
        self.six_yard_bottom = self.center_width - (neg_if_inverted * self.six_yard_width / 2)
        self.six_yard_top = self.center_width + (neg_if_inverted * self.six_yard_width / 2)
        self.goal_bottom = self.center_width - (neg_if_inverted * self.goal_width / 2)
        self.goal_top = self.center_width + (neg_if_inverted * self.goal_width / 2)           
        self.six_yard_left = self.six_yard_length
        self.six_yard_right = self.right - self.six_yard_length


@dataclass
class FixedDims(BaseDims):
    def __post_init__(self):
        self.setup_dims()


@dataclass
class VariableCenterDims(BaseDims):
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.left = - self.pitch_length / 2
        self.right = - self.left
        self.bottom = - self.pitch_width / 2
        self.top = - self.bottom
        self.width = self.pitch_width
        self.length = self.pitch_length
        self.six_yard_left = self.left + self.six_yard_length
        self.six_yard_right = - self.six_yard_left
        self.penalty_left = self.left + penalty_spot_distance
        self.penalty_right = self.right - penalty_spot_distance
        self.penalty_area_left = self.left + self.penalty_area_length
        self.penalty_area_right = - self.penalty_area_left
        self.setup_dims()


@dataclass
class CustomDims(BaseDims):
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.top = self.pitch_width
        self.right = self.pitch_length
        self.center_width = self.pitch_width / 2
        self.center_length = self.pitch_length / 2
        self.penalty_left = penalty_spot_distance
        self.penalty_box_dims()
        self.setup_dims()


@dataclass
class MetricasportsDims(BaseDims):
    penalty_spot_distance: InitVar[float] = None

    def __post_init__(self, penalty_spot_distance):
        self.aspect = self.pitch_width / self.pitch_length
        self.six_yard_width = round(self.six_yard_width / self.pitch_width, 4)
        self.six_yard_length = round(self.six_yard_length / self.pitch_length, 4)
        self.penalty_area_width = round(self.penalty_area_width / self.pitch_width, 4)
        self.penalty_area_length = round(self.penalty_area_length / self.pitch_length, 4)
        self.goal_length = round(self.goal_length / self.pitch_length, 4)
        self.goal_width = round(self.goal_width / self.pitch_width, 4)
        self.penalty_left = round(penalty_spot_distance / self.pitch_length, 4)
        self.penalty_box_dims()
        self.setup_dims()


def opta_dims():
    return FixedDims(left=0., right=100., bottom=0., top=100., aspect=68 / 105, width=100., length=100.,
                     pitch_width=68., pitch_length=105., goal_width=10.76, goal_length=1.9, goal_bottom=44.62,
                     goal_top=55.38, six_yard_width=26.4, six_yard_length=5.8, six_yard_left=5.8,
                     six_yard_right=94.2, six_yard_bottom=36.8, six_yard_top=63.2, penalty_left=11.5,
                     penalty_right=88.5, penalty_area_width=57.8, penalty_area_length=17.0, penalty_area_left=17.,
                     penalty_area_right=83., penalty_area_bottom=21.1, penalty_area_top=78.9,
                     center_width=50., center_length=50., circle_diameter=17.68, arc=None,
                     invert_y=False, origin_center=False)


def wyscout_dims():
    return FixedDims(left=0., right=100., bottom=100., top=0., aspect=68 / 105, width=100., length=100.,
                     pitch_width=68., pitch_length=105., goal_width=12., goal_length=1.9, goal_bottom=56., goal_top=44.,
                     six_yard_width=26., six_yard_length=6., six_yard_left=6., six_yard_right=94., six_yard_bottom=63.,
                     six_yard_top=37., penalty_left=10., penalty_right=90., penalty_area_width=62.,
                     penalty_area_length=16., penalty_area_left=16., penalty_area_right=84., penalty_area_bottom=81.,
                     penalty_area_top=19., center_width=50., center_length=50., circle_diameter=17.68, arc=None,
                     invert_y=True, origin_center=False)


def uefa_dims():
    return FixedDims(left=0., right=105., top=68., bottom=0., aspect=1., width=68., length=105., pitch_width=68.,
                     pitch_length=105., goal_width=7.32, goal_length=2., goal_bottom=30.34, goal_top=37.66,
                     six_yard_width=18.32, six_yard_length=5.5, six_yard_left=5.5, six_yard_right=99.5,
                     six_yard_bottom=24.84, six_yard_top=43.16, penalty_left=11., penalty_right=94.,
                     penalty_area_width=40.32, penalty_area_length=16.5, penalty_area_left=16.5,
                     penalty_area_right=88.5, penalty_area_bottom=13.84, penalty_area_top=54.16, center_width=34.,
                     center_length=52.5, circle_diameter=18.3, arc=53.05, invert_y=False, origin_center=False)


def statsbomb_dims():
    return FixedDims(left=0., right=120., bottom=80., top=0., aspect=1., width=80., length=120., pitch_width=80.,
                     pitch_length=120., goal_width=8., goal_length=2.4, goal_bottom=44., goal_top=36.,
                     six_yard_width=20., six_yard_length=6., six_yard_left=6., six_yard_right=114.,
                     six_yard_bottom=50., six_yard_top=30., penalty_left=12., penalty_right=108.,
                     penalty_area_width=44., penalty_area_length=18., penalty_area_left=18.,
                     penalty_area_right=102., penalty_area_bottom=62., penalty_area_top=18., center_width=40.,
                     center_length=60., circle_diameter=20., arc=53.05, invert_y=True, origin_center=False)


def metricasports_dims(pitch_width, pitch_length):
    return MetricasportsDims(top=0., bottom=1., left=0., right=1., pitch_width=pitch_width, pitch_length=pitch_length,
                             width=1., center_width=0.5, length=1., center_length=0.5, six_yard_width=18.32,
                             six_yard_length=5.5, penalty_spot_distance=11., penalty_area_width=40.32,
                             penalty_area_length=16.5, circle_diameter=18.3, goal_length=2., goal_width=7.32,
                             arc=None, invert_y=True, origin_center=False)


def skillcorner_secondspectrum_dims(pitch_width, pitch_length):
    return VariableCenterDims(aspect=1., pitch_width=pitch_width, pitch_length=pitch_length, goal_width=7.32,
                              goal_length=2., goal_bottom=-3.66, goal_top=3.66, six_yard_width=18.32,
                              six_yard_length=5.5, six_yard_bottom=-9.16, six_yard_top=9.16,
                              penalty_spot_distance=11., penalty_area_width=40.32, penalty_area_length=16.5,
                              penalty_area_bottom=-20.16, penalty_area_top=20.16, center_width=0., center_length=0.,
                              circle_diameter=18.3, arc=53.05, invert_y=False, origin_center=True)


def tracab_dims(pitch_width, pitch_length):
    return VariableCenterDims(aspect=1., pitch_width=pitch_width, pitch_length=pitch_length, goal_width=732.,
                              goal_length=200., goal_bottom=-366., goal_top=366., six_yard_width=1832.,
                              six_yard_length=550., six_yard_bottom=-916., six_yard_top=916.,
                              penalty_spot_distance=1100., penalty_area_width=4032., penalty_area_length=1650.,
                              penalty_area_bottom=-2016., penalty_area_top=2016., center_width=0., center_length=0.,
                              circle_diameter=1830., arc=53.05, invert_y=False, origin_center=True)


def custom_dims(pitch_width, pitch_length):
    return CustomDims(bottom=0., left=0., aspect=1., width=pitch_width, length=pitch_length, pitch_length=pitch_length,
                      pitch_width=pitch_width, six_yard_width=18.32, six_yard_length=5.5, penalty_area_width=40.32,
                      penalty_spot_distance=11., penalty_area_length=16.5, circle_diameter=18.3, goal_length=2.,
                      goal_width=7.32, arc=53.05, invert_y=False, origin_center=False)


def create_pitch_dims(pitch_type, pitch_width=None, pitch_length=None):
    if pitch_type == 'opta':
        spec = opta_dims()
    elif pitch_type == 'wyscout':
        spec = wyscout_dims()
    elif pitch_type == 'uefa':
        spec = uefa_dims()
    elif pitch_type == 'statsbomb':
        spec = statsbomb_dims()
    elif pitch_type == 'metricasports':
        spec = metricasports_dims(pitch_width, pitch_length)
    elif pitch_type in ['skillcorner', 'secondspectrum']:
        spec = skillcorner_secondspectrum_dims(pitch_width, pitch_length)
    elif pitch_type == 'tracab':
        pitch_width = pitch_width * 100.
        pitch_length = pitch_length * 100.
        spec = tracab_dims(pitch_width, pitch_length)
    else:
        spec = custom_dims(pitch_width, pitch_length)
    return spec
