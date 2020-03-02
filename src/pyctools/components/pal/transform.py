#!/usr/bin/env python
#  Pyctools-pal - PAL coding and decoding with Pyctools.
#  http://github.com/jim-easterbrook/pyctools-pal
#  Copyright (C) 2014-18  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

__all__ = ['FTFilterUV', 'FTFilterUV_2Dthresh', 'PostFilterUV']

import math

import numpy

from pyctools.components.interp.filtergenerator import FilterGeneratorCore
from pyctools.components.interp.resize import Resize
from pyctools.core.base import Transformer
from pyctools.core.config import ConfigEnum, ConfigFloat, ConfigInt
from pyctools.core.frame import Frame
from pyctools.core.types import pt_complex, pt_float
from .transformcore import transform_filter


class FTFilterUV(Transformer):
    """Filter modulated Cb,Cr in the Fourier Transform domain.

    This is the clever bit of the Transform PAL decoder.

    """
    inputs = ['input', 'threshold']

    def initialise(self):
        self.config['xtile'] = ConfigInt(min_value=8)
        self.config['ytile'] = ConfigInt(min_value=8)
        self.config['mode'] = ConfigEnum(choices=('limit', 'thresh', '2Dthresh'))
        self.config['threshold'] = ConfigFloat(min_value=0.0)
        self.config['slope'] = ConfigFloat()
        self.threshold_frame = None
        self.threshold_values = numpy.zeros((1, 1), dtype=pt_float)

    def on_start(self):
        self.update_config()
        if (self.config['mode'] != '2Dthresh' and
                            not self.input_buffer['threshold'].available()):
            # create null threshold frame and put it on input queue so
            # we don't wait for one to arrive
            self.threshold_frame = Frame()
            self.threshold(self.threshold_frame)

    def get_threshold(self):
        new_threshold = self.input_buffer['threshold'].peek()
        if new_threshold == self.threshold_frame:
            return True
        threshold_values = new_threshold.as_numpy(dtype=numpy.float32)
        if threshold_values.ndim != 2:
            self.logger.warning('Threshold input must be 2 dimensional')
            return False
        x_tile = self.config['xtile']
        y_tile = self.config['ytile']
        xlen = 1 + (x_tile // 8)
        ylen = y_tile
        if threshold_values.shape != (ylen, xlen):
            self.logger.warning(
                'Threshold input dimensions must be %d x %d', ylen, xlen)
            return False
        self.threshold_frame = new_threshold
        self.threshold_values = numpy.zeros((y_tile, x_tile), dtype=pt_float)
        for x in range(xlen):
            x_out = x + (x_tile // 8)
            for y in range(ylen):
                self.threshold_values[y, x_out] = threshold_values[y, x]
        return True

    def transform(self, in_frame, out_frame):
        self.update_config()
        x_tile = self.config['xtile']
        y_tile = self.config['ytile']
        mode = self.config['mode']
        threshold = self.config['threshold']
        slope = self.config['slope']
        if mode == '2Dthresh' and not self.get_threshold():
            return False
        in_data = in_frame.as_numpy(dtype=pt_complex)
        x_len = in_data.shape[1]
        y_len = in_data.shape[0]
        x_blk = x_len // x_tile
        y_blk = y_len // y_tile
        in_data = in_data.reshape(y_blk, y_tile, x_blk, x_tile)
        out_data = numpy.zeros(in_data.shape, dtype=pt_complex)
        transform_filter(out_data, in_data,
                         ord(mode[0]), slope, threshold, self.threshold_values)
        out_data = out_data.reshape(y_len, x_len, 1)
        audit = out_frame.metadata.get('audit')
        audit += 'data = TransformFilter(data)\n'
        audit += '    tile size: %d x %d\n' % (y_tile, x_tile)
        audit += '    mode: %s, threshold: %g, slope: %g\n' % (
            mode, threshold, slope)
        out_frame.metadata.set('audit', audit)
        out_frame.data = out_data
        return True


class FTFilterUV_2Dthresh(FTFilterUV):
    def __init__(self, config={}, **kwds):
        super(FTFilterUV_2Dthresh, self).__init__(
            xtile=32, ytile=16, mode='2Dthresh', config=config, **kwds)
        threshold = Frame()
        threshold.data = numpy.array(
            [[6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6],
             [6, 6, 6, 6, 6]], dtype=numpy.float32) / numpy.float32(10.0)
        threshold.type = 'thresh'
        audit = threshold.metadata.get('audit')
        audit += 'data = transform PAL decoder thresholds\n'
        threshold.metadata.set('audit', audit)
        self.threshold(threshold)


class PostFilterUV(Resize):
    """Chrominance post filter.

    Low pass filter, cutting at 1/2 fsc.

    """
    def __init__(self, config={}, **kwds):
        super(PostFilterUV, self).__init__(config=config, **kwds)
        self.filter(FilterGeneratorCore(x_ap=16, x_cut=25))
