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

__all__ = ['Decoder', 'CtoUV', 'PostFilterY', 'PostFilterUV']

import numpy

from pyctools.core.compound import Compound
from pyctools.core.frame import Frame
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.colourspace.yuvtorgb import YUVtoRGB
from pyctools.components.interp.resize import Resize

from .common import ModulateUV

class CtoUV(Matrix):
    """Matrix chroma to modulated Cb,Cr.

    This includes level conversions as specified in the "White Book".

    """
    def __init__(self, config={}, **kwds):
        super(CtoUV, self).__init__(config=config, **kwds)
        mat = Frame()
        mat.data = numpy.array(
            [[2.02 / 0.886], [1.14 / 0.701]], dtype=numpy.float32)
        mat.type = 'mat'
        audit = mat.metadata.get('audit')
        audit += 'data = PAL -> CbCr matrix\n'
        audit += '    values: %s\n' % (str(mat.data))
        mat.metadata.set('audit', audit)
        self.matrix(mat)


class PostFilterY(Resize):
    """Poor quality PAL "notch" filter.

    """
    def __init__(self, config={}, **kwds):
        super(PostFilterY, self).__init__(config=config, **kwds)
        fil = Frame()
        fil.data = numpy.array(
            [27, -238, 47, 238, 876, 238, 47, -238, 27],
            dtype=numpy.float32).reshape(1, -1, 1) / 1024.0
        fil.type = 'fil'
        audit = fil.metadata.get('audit')
        audit += 'data = Y notch filter\n'
        fil.metadata.set('audit', audit)
        self.filter(fil)


class PostFilterUV(Resize):
    """PAL decoder chrominance post filter.

    """
    def __init__(self, config={}, **kwds):
        super(PostFilterUV, self).__init__(config=config, **kwds)
        fil = Frame()
        fil.data = numpy.array(
            [1, 6, 19, 42, 71, 96, 106, 96, 71, 42, 19, 6, 1],
            dtype=numpy.float32).reshape(1, -1, 1) / 576.0
        fil.type = 'fil'
        audit = fil.metadata.get('audit')
        audit += 'data = UV low pass filter\n'
        fil.metadata.set('audit', audit)
        self.filter(fil)


class Decoder(Compound):
    """Conventional PAL decoder.

    The input is assumed to be sampled at 4 fsc, which will generate an
    output sampled at 13.5 MHz (Rec 601). This is a "simple" decoder
    with no line delay filtering to prevent "Hannover bars".

    """
    def __init__(self, config={}, **kwds):
        super(Decoder, self).__init__(
            setlevel = Arithmetic(
                func='((data - pt_float(64)) * pt_float(219.0 / 140.0)) + pt_float(16)'),
            filterY = PostFilterY(),
            yuvrgb = YUVtoRGB(matrix='601'),
            matrix = CtoUV(),
            demod = ModulateUV(),
            filterUV = PostFilterUV(),
            linkages = {
                ('self',     'input')   : [('setlevel', 'input')],
                ('setlevel', 'output')  : [('filterY',  'input'),
                                           ('matrix',   'input')],
                ('filterY',  'output')  : [('yuvrgb',   'input_Y')],
                ('matrix',   'output')  : [('demod',    'input')],
                ('demod',    'output')  : [('filterUV', 'input')],
                ('filterUV', 'output')  : [('yuvrgb',   'input_UV')],
                ('yuvrgb',   'output')  : [('self',     'output')],
                },
            config=config, **kwds)
