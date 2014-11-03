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

"""Normal PAL coder components.

Converts RGB pictures to PAL. Input is assumed to be sampled at
13.5MHz. Other formats (e.g. HDTV) will work but not make a legitimate
PAL picture.

"""

__all__ = ['Coder', 'PreFilterUV', 'ToPAL']

import numpy

from pyctools.core import Compound, Frame
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.interp.gaussianfilter import GaussianFilterCore
from pyctools.components.interp.resize import Resize

from .common import ModulateUV

def PreFilterUV():
    filter_Y = numpy.array([[1.0]], dtype=numpy.float32)
    filter_UV = GaussianFilterCore(x_sigma=1.659)
    out_frame = Frame()
    out_frame.data = [filter_Y, filter_UV.data[0], filter_UV.data[0]]
    out_frame.type = 'fil'
    audit = out_frame.metadata.get('audit')
    audit += 'data = 3-component filter\n'
    audit += '    Y filter = [[1.0]], U/V filter = {\n%s}\n' % (
        filter_UV.metadata.get('audit'))
    out_frame.metadata.set('audit', audit)
    resize = Resize()
    resize.filter(out_frame)
    return resize

def ToPAL():
    out_frame = Frame()
    out_frame.data = [numpy.array(
        [[1.0, 2.0 * 0.886 / 2.02, 2.0 * 0.701 / 1.14]], dtype=numpy.float32)]
    out_frame.type = 'mat'
    audit = out_frame.metadata.get('audit')
    audit += 'data = YCbCr -> PAL matrix\n'
    audit += '    values: %s\n' % (str(out_frame.data[0]))
    out_frame.metadata.set('audit', audit)
    matrix = Matrix()
    matrix.matrix(out_frame)
    return matrix

def Coder():
    prefilter = PreFilterUV()
    modulator = ModulateUV()
    merge = ToPAL()
    setlevel = Arithmetic()
    cfg = setlevel.get_config()
    cfg['func'] = '((data - 16.0) * (140.0 / 219.0)) + 64.0'
    setlevel.set_config(cfg)
    return Compound(
        prefilter = prefilter,
        modulator = modulator,
        merge = merge,
        setlevel = setlevel,
        linkages = {
            ('self',      'input')  : ('prefilter', 'input'),
            ('prefilter', 'output') : ('modulator', 'input'),
            ('modulator', 'output') : ('merge',     'input'),
            ('merge',     'output') : ('setlevel',  'input'),
            ('setlevel',  'output') : ('self',      'output'),
            }
        )
