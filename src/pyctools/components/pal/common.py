#!/usr/bin/env python
#  Pyctools-pal - PAL coding and decoding with Pyctools.
#  http://github.com/jim-easterbrook/pyctools-pal
#  Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
#  This program is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.

"""Common components.

"""

__all__ = ['To4Fsc', 'From4Fsc', 'ModulateUV']

import math

import numpy

from pyctools.core import Frame
from pyctools.components.interp.filtergenerator import FilterGeneratorCore
from pyctools.components.interp.resize import Resize
from pyctools.components.modulate.modulate import Modulate

def To4Fsc():
    # 4fsc = 922 active samples/line, Rec 601 = 702 active samples/line
    xup, xdown = 461, 351
    resize = Resize()
    cfg = resize.get_config()
    cfg['xup'] = xup
    cfg['xdown'] = xdown
    resize.set_config(cfg)
    resize.filter(FilterGeneratorCore(x_up=xup, x_down=xdown, x_ap=16))
    return resize

def From4Fsc():
    # 4fsc = 922 active samples/line, Rec 601 = 702 active samples/line
    xup, xdown = 351, 461
    resize = Resize()
    cfg = resize.get_config()
    cfg['xup'] = xup
    cfg['xdown'] = xdown
    resize.set_config(cfg)
    resize.filter(FilterGeneratorCore(x_up=xup, x_down=xdown, x_ap=16))
    return resize

def ModulateUV():
    cell_Y = numpy.array([[[1.0]]], dtype=numpy.float32)
    cell_U = numpy.empty([4, 8, 4], dtype=numpy.float32)
    cell_V = numpy.empty([4, 8, 4], dtype=numpy.float32)
    for z in range(cell_U.shape[0]):
        for y in range(cell_U.shape[1]):
            v_axis_switch = (((((y + 1) // 2) + z) % 2) * 2) - 1
            for x in range(cell_U.shape[2]):
                phase = 0.75 + float((x - (y // 2) + (y % 2) - z) % 4) / 2.0
                phase *= v_axis_switch
                cell_U[z, y, x] = math.cos(math.pi * phase)
                cell_V[z, y, x] = math.sin(math.pi * phase)
    modulate = Modulate()
    out_frame = Frame()
    out_frame.data = [cell_Y, cell_U, cell_V]
    out_frame.type = 'cell'
    audit = out_frame.metadata.get('audit')
    audit += 'data = 3-component modulation cell\n'
    audit += '    Y cell = unity, U/V cell = PAL subcarrier\n'
    out_frame.metadata.set('audit', audit)
    modulate.cell(out_frame)
    return modulate
