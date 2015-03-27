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

__all__ = ['Coder', 'PreFilterUV', 'ToPAL', 'UVtoC']

import numpy

from pyctools.core.compound import Compound
from pyctools.core.frame import Frame
from pyctools.components.adder import Adder
from pyctools.components.arithmetic import Arithmetic
from pyctools.components.colourspace.rgbtoyuv import RGBtoYUV
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.interp.gaussianfilter import GaussianFilterCore
from pyctools.components.interp.resize import Resize
from pyctools.components.plumbing.collator import Collator

from .common import ModulateUV

def PreFilterUV():
    resize = Resize()
    resize.filter(GaussianFilterCore(x_sigma=1.659))
    return resize

def ToPAL():
    out_frame = Frame()
    out_frame.data = numpy.array(
        [[1.0, 2.0 * 0.886 / 2.02, 2.0 * 0.701 / 1.14]], dtype=numpy.float32)
    out_frame.type = 'mat'
    audit = out_frame.metadata.get('audit')
    audit += 'data = YCbCr -> PAL matrix\n'
    audit += '    values: %s\n' % (str(out_frame.data))
    out_frame.metadata.set('audit', audit)
    matrix = Matrix()
    matrix.matrix(out_frame)
    return matrix

def UVtoC():
    mat = Frame()
    mat.data = numpy.array(
        [[2.0 * 0.886 / 2.02, 2.0 * 0.701 / 1.14]], dtype=numpy.float32)
    mat.type = 'mat'
    audit = mat.metadata.get('audit')
    audit += 'data = Modulated CbCr -> PAL chroma matrix\n'
    audit += '    values: %s\n' % (str(mat.data))
    mat.metadata.set('audit', audit)
    matrix = Matrix()
    matrix.matrix(mat)
    return matrix

def Coder():
    return Compound(
        rgbyuv = RGBtoYUV(config={'outframe_pool_len' : 5, 'matrix' : '601'}),
        adder = Adder(),
        prefilter = PreFilterUV(),
        modulator = ModulateUV(),
        matrix = UVtoC(),
        setlevel = Arithmetic(config={
            'func' : '((data - pt_float(16.0)) * pt_float(140.0 / 219.0)) + pt_float(64.0)'}),
        linkages = {
            ('self',      'input')     : [('rgbyuv',    'input')],
            ('rgbyuv',    'output_Y')  : [('adder',     'input0')],
            ('rgbyuv',    'output_UV') : [('prefilter', 'input')],
            ('prefilter', 'output')    : [('modulator', 'input')],
            ('modulator', 'output')    : [('matrix',    'input')],
            ('matrix',    'output')    : [('adder',     'input1')],
            ('adder',     'output')    : [('setlevel',  'input')],
            ('setlevel',  'output')    : [('self',      'output')],
            }
        )
