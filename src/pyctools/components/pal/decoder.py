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

__all__ = ['Decoder', 'FromPAL']

import numpy

from pyctools.core import Compound, Frame
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.interp.gaussianfilter import GaussianFilterCore
from pyctools.components.interp.resize import Resize

from .common import ModulateUV

def FromPAL():
    out_frame = Frame()
    out_frame.data = [numpy.array(
        [[1.0], [2.02 / 0.886], [1.14 / 0.701]], dtype=numpy.float32)]
    out_frame.type = 'mat'
    audit = out_frame.metadata.get('audit')
    audit += 'data = PAL -> YCbCr matrix\n'
    audit += '    values: %s\n' % (str(out_frame.data[0]))
    out_frame.metadata.set('audit', audit)
    matrix = Matrix()
    matrix.matrix(out_frame)
    return matrix

def PostFilter():
    filter_Y = numpy.array(
        [[27, -238, 47, 238, 876, 238, 47, -238, 27]],
        dtype=numpy.float32) / 1024.0
    filter_UV = numpy.array(
        [[1, 6, 19, 42, 71, 96, 106, 96, 71, 42, 19, 6, 1]],
        dtype=numpy.float32) / 576.0
    out_frame = Frame()
    out_frame.data = [filter_Y, filter_UV, filter_UV]
    out_frame.type = 'fil'
    audit = out_frame.metadata.get('audit')
    audit += 'data = 3-component filter\n'
    audit += '    Y filter = notch, U/V filter = lpf\n'
    out_frame.metadata.set('audit', audit)
    resize = Resize()
    resize.filter(out_frame)
    return resize

def Decoder():
    setlevel = Arithmetic()
    cfg = setlevel.get_config()
    cfg['func'] = '((data - 64.0) * (219.0 / 140.0)) + 16.0'
    setlevel.set_config(cfg)
    split = FromPAL()
    demod = ModulateUV()
    postfil = PostFilter()
    return Compound(
        setlevel = setlevel,
        split = split,
        demod = demod,
        postfil = postfil,
        linkages = {
            ('self',     'input')  : ('setlevel', 'input'),
            ('setlevel', 'output') : ('split',    'input'),
            ('split',    'output') : ('demod',    'input'),
            ('demod',    'output') : ('postfil',  'input'),
            ('postfil',  'output') : ('self',     'output'),
            }
        )
