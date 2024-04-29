# SPDX-FileCopyrightText: 2020 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_led_animation.tilegrid`
================================================================================

PixelGrid helper for 2D animations tiled.

* Author(s): Djair Guilherme

Implementation Notes
--------------------

**Hardware:**

* `Adafruit NeoPixels <https://www.adafruit.com/category/168>`_
* `Adafruit DotStars <https://www.adafruit.com/category/885>`_

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

"""
from micropython import const

from .helper import PixelMap

HORIZONTAL = const(1)
VERTICAL = const(2)


class TileGrid:
    """
    TileGrid lets you address a pixel strip with x and y coordinates.

    :param strip: An object that implements the Neopixel or Dotstar protocol.
    :param width: Grid width.
    :param height: Grid height.
    :param tile_num: Number of Tiles.
    
    :param orientation: Orientation of the strip pixels - HORIZONTAL (default) or VERTICAL.
    :param alternating: Whether the strip alternates direction from row to row (default True).
    :param reverse_x: Whether the strip X origin is on the right side (default False).
    :param reverse_y: Whether the strip Y origin is on the bottom (default False).
    :param tuple top: (x, y) coordinates of grid top left corner (Optional)
    :param tuple bottom: (x, y) coordinates of grid bottom right corner (Optional)

    """

    def __init__(
        self,
        strip,
        width, # of individual tile
        height, # of individual tile
        tile_num, # number of tiles
        orientation=HORIZONTAL,
        alternating=True,
        reverse_x=False,
        reverse_y=False,
        top=0,
        bottom=0,
    ):  # pylint: disable=too-many-arguments,too-many-locals
        self._pixels = strip
        self._x = []
        self.height = height
        self.width = width
        self.tile_num = tile_num

        if self.tile_num > 1:
          # This implements a mapper with correct grid for me
            mapper = generate_grid(self.width, self.height, self.tile_num)
            for m in mapper:
                self._x.append(
                    PixelMap(
                        strip,
                        m,
                        individual_pixels=True,
                    )
                )
        self.n = len(self._x)

    def __repr__(self):
        return "[" + ", ".join([str(self[x]) for x in range(self.n)]) + "]"

    def __setitem__(self, index, val):
        if isinstance(index, slice):
            raise NotImplementedError("PixelGrid does not support slices")

        if isinstance(index, tuple):
            self._x[index[0]][index[1]] = val
        else:
            raise ValueError("PixelGrid assignment needs a sub-index or x,y coordinate")

        if self._pixels.auto_write:
            self.show()

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise NotImplementedError("PixelGrid does not support slices")
        if index < 0:
            index += len(self)
        if index >= self.n or index < 0:
            raise IndexError("x is out of range")
        return self._x[index]

    def __len__(self):
        return self.n

    @property
    def brightness(self):
        """
        brightness from the underlying strip.
        """
        return self._pixels.brightness

    @brightness.setter
    def brightness(self, brightness):
        # pylint: disable=attribute-defined-outside-init
        self._pixels.brightness = min(max(brightness, 0.0), 1.0)

    def fill(self, color):
        """
        Fill the PixelGrid with the specified color.

        :param color: Color to use.
        """
        for strip in self._x:
            strip.fill(color)

    def show(self):
        """
        Shows the pixels on the underlying strip.
        """
        self._pixels.show()

    @property
    def auto_write(self):
        """
        auto_write from the underlying strip.
        """
        return self._pixels.auto_write

    @auto_write.setter
    def auto_write(self, value):
        self._pixels.auto_write = value
    
  
# Can't use this functions, because still don't see it working with my led stripe...

def reverse_x_mapper(width, mapper):
    """
    Returns a coordinate mapper function for grids with reversed X coordinates.

    :param width: width of strip
    :param mapper: grid mapper to wrap
    :return: mapper(x, y)
    """
    max_x = width - 1

    def x_mapper(x, y):
        return mapper(max_x - x, y)

    return x_mapper


def reverse_y_mapper(height, mapper):
    """
    Returns a coordinate mapper function for grids with reversed Y coordinates.

    :param height: width of strip
    :param mapper: grid mapper to wrap
    :return: mapper(x, y)
    """
    max_y = height - 1

    def y_mapper(x, y):
        return mapper(x, max_y - y)

    return y_mapper

# This is my custom grid generator. My Stripe has 32x8 and I need to make it work 32x16 with two of them

def generate_grid(width, height, tile_num): 
    def single_tile_coord():
        single_tile = []

        for i in range(width * height):
            group_index = i // height
            ascending = (group_index % 2) == 0
            number_within_group = i % height

            if ascending:
                number = group_index * height + number_within_group
            else:
                number = (group_index + 1) * height - 1 - number_within_group

            if number_within_group == 0:
                temp = []

            temp.append (number)

            if number_within_group == height - 1:
                single_tile.append(tuple(temp))

        return single_tile

    def multi_tile(original_matrix): 
        multi_temp = []
        factor = tile_num - 1
        
        if factor == 0:
            multi_temp = original_matrix
        else:
            for tup in original_matrix:
                modified_tuple = tup[:height]  

                for n in range (factor):
                    modified_tuple += tuple(num + (factor * (width * height)) for num in tup[:height])          
                    multi_temp.append(modified_tuple)

        return multi_temp

    default_tile = single_tile_coord()
    return multi_tile(default_tile) 

