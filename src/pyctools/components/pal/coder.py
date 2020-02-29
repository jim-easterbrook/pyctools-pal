#!/usr/bin/env python
#  Pyctools-pal - PAL coding and decoding with Pyctools.
#  http://github.com/jim-easterbrook/pyctools-pal
#  Copyright (C) 2014-20  Jim Easterbrook  jim@jim-easterbrook.me.uk
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

__all__ = ['Coder', 'PostFilterPAL', 'PreFilterUV', 'UVtoC']

import numpy

from pyctools.core.compound import Compound
from pyctools.core.frame import Frame
from pyctools.components.arithmetic import Arithmetic2
from pyctools.components.colourspace.rgbtoyuv import RGBtoYUV
from pyctools.components.colourspace.matrix import Matrix
from pyctools.components.interp.filterdesign import FilterDesign
from pyctools.components.interp.gaussianfilter import GaussianFilterCore
from pyctools.components.interp.resize import Resize

from .common import ModulateUV


class PreFilterUV(Resize):
    """Gaussian low-pass filter suitable for filtering chrominance
    before modulation.

    According to the "White Book" the chrominance shall be attenuated by
    <3 dB at 1.3 MHz and >20 dB at 4 MHz.

    """
    def __init__(self, config={}, **kwds):
        super(PreFilterUV, self).__init__(config=config, **kwds)
        self.filter(GaussianFilterCore(x_sigma=1.659))


class PostFilterPAL(Compound):
    """5.5 MHz low pass filter.

    According to the "White Book" the luminance shall be substantially
    uniform from 0 to 5.5 MHz. It needs to be attenuated at 6 MHz to
    leave space for the sound carrier.

    """
    def __init__(self, config={}, **kwds):
        super(PostFilterPAL, self).__init__(
            resize = Resize(),
            fildes = FilterDesign(
                frequency='0.0, 0.307, 0.317, 0.346, 0.356, 0.5',
                gain='     1.0, 1.0,   1.0,   0.0,   0.0,   0.0',
                weight='   1.0, 1.0,   0.0,   0.0,   1.0,   1.0',
                aperture=61,
                ),
            linkages = {
                ('self',   'input')    : [('resize', 'input')],
                ('fildes', 'filter')   : [('resize', 'filter')],
                ('resize', 'output')   : [('self',   'output')],
                ('fildes', 'response') : [('self',   'response')],
                },
            config=config, **kwds)


class UVtoC(Matrix):
    """Matrix modulated Cb,Cr to a single chroma component.

    This includes level conversions as specified in the "White Book".

    """
    def __init__(self, config={}, **kwds):
        super(UVtoC, self).__init__(config=config, **kwds)
        mat = Frame()
        mat.data = numpy.array(
            [[2.0 * 0.886 / 2.02, 2.0 * 0.701 / 1.14]], dtype=numpy.float32)
        mat.type = 'mat'
        audit = mat.metadata.get('audit')
        audit += 'data = Modulated CbCr -> PAL chroma matrix\n'
        audit += '    values: %s\n' % (str(mat.data))
        mat.metadata.set('audit', audit)
        self.matrix(mat)


class Coder(Compound):
    """Conventional PAL coder.

    The input is RGB, assumed to be Rec 601 13.5 MHz sampled. The output
    is sampled at 4 fsc. Other input sampling rates will work, but the
    output will not be a valid PAL signal.

    """
    def __init__(self, config={}, **kwds):
        super(Coder, self).__init__(
            rgbyuv = RGBtoYUV(outframe_pool_len=5, matrix='601'),
            prefilter = PreFilterUV(),
            modulator = ModulateUV(),
            matrix = UVtoC(),
            assemble = Arithmetic2(
                func='((data1 + data2) * pt_float(140.0 / 255.0)) + pt_float(64.0)'),
            postfilter = PostFilterPAL(),
            linkages = {
                ('self',       'input')     : [('rgbyuv',     'input')],
                ('rgbyuv',     'output_Y')  : [('assemble',   'input1')],
                ('rgbyuv',     'output_UV') : [('prefilter',  'input')],
                ('prefilter',  'output')    : [('modulator',  'input')],
                ('modulator',  'output')    : [('matrix',     'input')],
                ('matrix',     'output')    : [('assemble',   'input2')],
                ('assemble',   'output')    : [('postfilter', 'input')],
                ('postfilter', 'output')    : [('self',       'output')],
                ('prefilter',  'filter')    : [('self',       'pre_filt')],
                ('postfilter', 'response')  : [('self',       'post_resp')],
                },
            config=config, **kwds)
