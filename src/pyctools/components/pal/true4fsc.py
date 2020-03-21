#  Pyctools - a picture processing algorithm development kit.
#  http://github.com/jim-easterbrook/pyctools
#  Copyright (C) 2020  Pyctools contributors
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

__all__ = ['ToTrue4Fsc']
__docformat__ = 'restructuredtext en'

import sys
if 'sphinx' in sys.modules:
    __all__.append('resize_frame')

import numpy

from pyctools.core.config import ConfigInt
from pyctools.core.base import Transformer
from pyctools.components.interp.filtergenerator import FilterGenerator
from .true4fsccore import resize_frame


class ToTrue4Fsc(Transformer):
    """Convert "Rec 601" sampled image to 4 fsc sampling.

    Unlike the :py:class:`~.common.To4Fsc` component this uses the
    correct non-orthogonal sampling structure. (4 fsc has 1135.0064
    samples per line.) This is important if you want to process pictures
    that have been through real PAL hardware. Otherwise the simpler
    orthogonal sampling structure is good enough.

    =========  ===  ====
    Config
    =========  ===  ====
    ``phase``  int  Adjust 4 fsc sampling phase -180 to 180 degrees.
    =========  ===  ====

    """
    def initialise(self):
        self.config.phase = ConfigInt(
            value=0, min_value=-180, max_value=180, wrapping=True)
        self.filter = None

    def transform(self, in_frame, out_frame):
        self.update_config()
        in_data = in_frame.as_numpy(dtype=numpy.float32)
        ylen, xlen, comps = in_data.shape
        if self.filter is None:
            if comps == 2:
                # assume UV is at half sampling rate
                self.x_down = 432
            else:
                self.x_down = 864
            # make a 1024 phase filter
            self.filter = FilterGenerator.core(
                x_up=1024, x_down=self.x_down, x_ap=16).as_numpy(dtype=numpy.float32)
            self.filter *= numpy.float32(1024)
            self.filter = self.filter.flatten()
            self.filter = numpy.pad(self.filter, (1, 0)).reshape((-1, 1024))
            self.filter = self.filter.swapaxes(0, 1)
        x_phase_inc = float(self.x_down) / 1135.0064
        y_phase_inc = -x_phase_inc * 0.0032
        phase_0 = float(self.config.phase) * x_phase_inc / 360.0
        out_data = numpy.zeros(
            (ylen, int(round(xlen * 1135 / self.x_down)), comps),
            dtype=numpy.float32)
        resize_frame(
            out_data, in_data, self.filter, phase_0, x_phase_inc, y_phase_inc)
        out_frame.data = out_data
        return True
