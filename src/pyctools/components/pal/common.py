#!/usr/bin/env python
#  Pyctools-pal - PAL coding and decoding with Pyctools.
#  http://github.com/jim-easterbrook/pyctools-pal
#  Copyright (C) 2014-20 Jim Easterbrook  jim@jim-easterbrook.me.uk
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

__all__ = ['To4Fsc', 'From4Fsc', 'ModulateUV']

import math

import numpy

from pyctools.core.compound import Compound
from pyctools.core.config import ConfigEnum, ConfigInt
from pyctools.core.frame import Frame
from pyctools.components.interp.imageresizer import ImageResizerX
from pyctools.components.modulate import Modulate


class To4Fsc(ImageResizerX):
    """Convert 13.5 MHz (Rec 601) sampled image to 4 fsc sampling.

    The conversion is not exact as 4 fsc is skewed by one pixel over a
    frame.

    """
    def __init__(self, config={}, **kwds):
        # 4fsc = 922 active samples/line, Rec 601 = 702 active samples/line
        cfg = {'up': 461, 'down': 351, 'aperture': 12}
        cfg.update(kwds)
        cfg.update(config)
        super(To4Fsc, self).__init__(config=config, **kwds)


class From4Fsc(ImageResizerX):
    """Convert 4 fsc sampled image to 13.5 MHz (Rec 601) sampling.

    The conversion is not exact as 4 fsc is skewed by one pixel over a
    frame.

    """
    def __init__(self, config={}, **kwds):
        # 4fsc = 922 active samples/line, Rec 601 = 702 active samples/line
        cfg = {'up': 351, 'down': 461, 'aperture': 12}
        cfg.update(kwds)
        cfg.update(config)
        super(From4Fsc, self).__init__(config=config, **kwds)


class ModulateUV(Modulate):
    """Modulate 4 fsc sampled Cb,Cr with PAL sub-carriers.

    The two components are modulated in quadrature, and the Cr
    modulation includes the V-axis switch.

    """
    def initialise(self):
        super(ModulateUV, self).initialise()
        self.config.sc_phase = ConfigInt(
            value=2, min_value=0, max_value=3, wrapping=True)
        self.config.VAS_phase = ConfigEnum(choices=('-1', '1'), value='1')

    def on_set_config(self):
        super(ModulateUV, self).on_set_config()
        self.update_config()
        # phase is in "quarter cycles"
        phase = float(self.config.sc_phase) + 0.5
        v_axis_switch = int(self.config.VAS_phase)
        cell = numpy.empty([4, 8, 4, 2], dtype=numpy.float32)
        for z in range(cell.shape[0]):
            for f in range(2):
                for y in range(f, cell.shape[1], 2):
                    phase = phase % 4
                    for x in range(cell.shape[2]):
                        cell[z, y, x, 0] = math.sin(phase * math.pi / 2.0)
                        cell[z, y, x, 1] = math.cos(phase * math.pi / 2.0) * v_axis_switch
                        # 4 fsc sampling, so fsc advances by 1/4 cycle per sample
                        phase += 1
                    # "quarter line offset" retards by 1/4 cycle per field line
                    phase -= 1
                    v_axis_switch *= -1
                # 313 lines in 1st field, 312 lines in 2nd
                if f == 0:
                    remainder = 313 - (cell.shape[1] // 2)
                else:
                    remainder = 312 - (cell.shape[1] // 2)
                phase -= remainder
                if remainder % 2:
                    v_axis_switch *= -1
                # "25 Hz offset" adds 1/2 cycle per field period
                phase += 2
        cell_frame = Frame()
        cell_frame.data = cell
        cell_frame.type = 'cell'
        audit = cell_frame.metadata.get('audit')
        audit += 'data = PAL subcarrier modulation cell\n'
        cell_frame.metadata.set('audit', audit)
        self.cell(cell_frame)
