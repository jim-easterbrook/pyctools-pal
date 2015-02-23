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

"""Normal PAL decoder components.

"""

__all__ = ['Decoder', 'FromPAL', 'PostFilterY', 'PostFilterUV']

import numpy

from pyctools.core.compound import Compound
from pyctools.core.frame import Frame
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.colourspace.yuvtorgb import YUVtoRGB
from pyctools.components.interp.resize import Resize

from .common import ModulateUV

def FromPAL():
    out_frame = Frame()
    out_frame.data = numpy.array(
        [[2.02 / 0.886], [1.14 / 0.701]], dtype=numpy.float32)
    out_frame.type = 'mat'
    audit = out_frame.metadata.get('audit')
    audit += 'data = PAL -> CbCr matrix\n'
    audit += '    values: %s\n' % (str(out_frame.data))
    out_frame.metadata.set('audit', audit)
    matrix = Matrix()
    matrix.matrix(out_frame)
    return matrix

def PostFilterY():
    filter_Y = numpy.array(
        [27, -238, 47, 238, 876, 238, 47, -238, 27],
        dtype=numpy.float32).reshape(1, -1, 1) / 1024.0
    out_frame = Frame()
    out_frame.data = filter_Y
    out_frame.type = 'fil'
    audit = out_frame.metadata.get('audit')
    audit += 'data = Y notch filter\n'
    out_frame.metadata.set('audit', audit)
    resize = Resize()
    resize.filter(out_frame)
    return resize

def PostFilterUV():
    filter_UV = numpy.array(
        [1, 6, 19, 42, 71, 96, 106, 96, 71, 42, 19, 6, 1],
        dtype=numpy.float32).reshape(1, -1, 1) / 576.0
    out_frame = Frame()
    out_frame.data = filter_UV
    out_frame.type = 'fil'
    audit = out_frame.metadata.get('audit')
    audit += 'data = UV low pass filter\n'
    out_frame.metadata.set('audit', audit)
    resize = Resize()
    resize.filter(out_frame)
    return resize

def Decoder():
    return Compound(
        setlevel = Arithmetic(
            func='((data - pt_float(64)) * pt_float(219.0 / 140.0)) + pt_float(16)'),
        filterY = PostFilterY(),
        yuvrgb = YUVtoRGB(matrix='601'),
        matrix = FromPAL(),
        demod = ModulateUV(),
        filterUV = PostFilterUV(),
        linkages = {
            ('self',     'input')   : ('setlevel', 'input'),
            ('setlevel', 'output')  : ('filterY',  'input',
                                       'matrix',   'input'),
            ('filterY',  'output')  : ('yuvrgb',   'input_Y'),
            ('matrix',   'output')  : ('demod',    'input'),
            ('demod',    'output')  : ('filterUV', 'input'),
            ('filterUV', 'output')  : ('yuvrgb',   'input_UV'),
            ('yuvrgb',   'output')  : ('self',     'output'),
            }
        )
