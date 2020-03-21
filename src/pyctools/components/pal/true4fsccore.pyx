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

from __future__ import absolute_import

from cython.parallel import prange
import numpy as np

cimport cython
cimport numpy

DTYPE = np.float32
ctypedef numpy.float32_t DTYPE_t

@cython.boundscheck(False)
cdef void resize_line(DTYPE_t[:, :] out_line,
                      DTYPE_t[:, :] in_line,
                      DTYPE_t[:, :] norm_filter,
                      double x_phase_inc, double phase_0) nogil:
    cdef:
        unsigned int xlen_in, xlen_out, xlen_fil, x_in, x_out, x_fil
        unsigned int comps, c
        int x_in_0, x_fil_off
        int fil_phases, phase
        DTYPE_t acc
        double d_phase
    xlen_in = in_line.shape[0]
    xlen_out = out_line.shape[0]
    xlen_fil = norm_filter.shape[1]
    fil_phases = norm_filter.shape[0]
    comps = out_line.shape[1]
    # offset to get to centre of filter
    x_fil_off = xlen_fil // 2
    for c in range(comps):
        d_phase = phase_0
        x_in_0 = x_fil_off
        while d_phase < 1.0:
            d_phase += 1.0
            x_in_0 -= 1
        for x_out in range(xlen_out):
            while d_phase >= 1.0:
                d_phase -= 1.0
                x_in_0 += 1
            phase = <int>(d_phase * fil_phases)
            x_in = x_in_0
            acc = out_line[x_out, c]
            for x_fil in range(xlen_fil):
                if x_in < xlen_in:
                    acc += in_line[x_in, c] * norm_filter[phase, x_fil]
                x_in -= 1
                if x_in < 0:
                    break
            out_line[x_out, c] = acc
            d_phase += x_phase_inc

@cython.boundscheck(False)
cdef void resize_frame_core(DTYPE_t[:, :, :] out_frame,
                            DTYPE_t[:, :, :] in_frame,
                            DTYPE_t[:, :] norm_filter,
                            double phase_0,
                            double x_phase_inc, double y_phase_inc):
    cdef:
        int ylen
        int y
        double phase
    with nogil:
        ylen = in_frame.shape[0]
        for y in prange(ylen, schedule='static'):
            phase = phase_0 + (y_phase_inc * <double>y)
            resize_line(out_frame[y], in_frame[y], norm_filter,
                        x_phase_inc, phase)

def resize_frame(numpy.ndarray[DTYPE_t, ndim=3] out_frame,
                 numpy.ndarray[DTYPE_t, ndim=3] in_frame,
                 numpy.ndarray[DTYPE_t, ndim=2] norm_filter,
                 float phase_0, float x_phase_inc, float y_phase_inc):
    """Filter and horizontally resize a single frame.

    The filter should be a 2D array. The outer dimension is the number
    of filter phases, which should be at least 256, and the inner
    dimension is the aperture of the filter. Each phase should be
    normalised so the coefficients sum to unity.

    :param numpy.ndarray out_frame: Output image, initialised to zero.

    :param numpy.ndarray in_frame: Input image.

    :param numpy.ndarray norm_filter: Normalised filter.

    :param float phase_0: Sampling phase of the first sample in output pixels.

    :param float x_phase_inc: Amount to increment the phase each horizontal pixel.

    :param float y_phase_inc: Amount to increment the phase each picture line.

    """
    resize_frame_core(out_frame, in_frame, norm_filter,
                      phase_0, x_phase_inc, y_phase_inc)
