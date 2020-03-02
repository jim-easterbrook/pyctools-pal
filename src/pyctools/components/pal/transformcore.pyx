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

cimport cython
cimport numpy

ctypedef numpy.complex64_t CMPLX_t
ctypedef numpy.float32_t FLOAT_t

def transform_filter(numpy.ndarray[CMPLX_t, ndim=4] out_data,
                     numpy.ndarray[CMPLX_t, ndim=4] in_data,
                     char mode, FLOAT_t slope, FLOAT_t threshold,
                     numpy.ndarray[FLOAT_t, ndim=2] threshold_values):
    cdef:
        unsigned int x_blk, y_blk, x_tile, y_tile
        unsigned int i, j, x, y, x_conj, y_conj, x_ref, y_ref
        CMPLX_t in_val, ref_val
        FLOAT_t adj, m_in, m_ref
    y_blk = out_data.shape[0]
    y_tile = out_data.shape[1]
    x_blk = out_data.shape[2]
    x_tile = out_data.shape[3]
    for y in range(y_tile):
        y_ref = ((y_tile // 2) + y_tile - y) % y_tile
        for x in range(x_tile // 8, 1 + (x_tile // 4)):
            adj = 1.0 - (slope * (x - (x_tile // 4)) / x_tile)
            x_ref = (x_tile // 2) - x
            if x == x_ref and y == y_ref:
                for j in range(y_blk):
                    for i in range(x_blk):
                        out_data[j, y, i, x] = in_data[j, y, i, x]
            elif mode == 'l':
                for j in range(y_blk):
                    for i in range(x_blk):
                        in_val = in_data[j, y, i, x]
                        ref_val = in_data[j, y_ref, i, x_ref]
                        m_in = abs(in_val) * adj
                        m_ref = abs(ref_val) / adj
                        if m_in < m_ref:
                            out_data[j, y, i, x] = in_val
                            out_data[j, y_ref, i, x_ref] = ref_val * m_in / m_ref
                        else:
                            out_data[j, y, i, x] = in_val * m_ref / m_in
                            out_data[j, y_ref, i, x_ref] = ref_val
            elif mode == '2':
                for j in range(y_blk):
                    for i in range(x_blk):
                        in_val = in_data[j, y, i, x]
                        ref_val = in_data[j, y_ref, i, x_ref]
                        m_in = abs(in_val) * adj
                        m_ref = abs(ref_val) / adj
                        if (m_in > m_ref * threshold_values[y, x] and
                                m_ref > m_in * threshold_values[y, x]):
                            out_data[j, y, i, x] = in_val
                            out_data[j, y_ref, i, x_ref] = ref_val
            else:
                for j in range(y_blk):
                    for i in range(x_blk):
                        in_val = in_data[j, y, i, x]
                        ref_val = in_data[j, y_ref, i, x_ref]
                        m_in = abs(in_val) * adj
                        m_ref = abs(ref_val) / adj
                        if (m_in > m_ref * threshold and
                                m_ref > m_in * threshold):
                            out_data[j, y, i, x] = in_val
                            out_data[j, y_ref, i, x_ref] = ref_val
    for y in range(y_tile):
        y_conj = (y_tile - y) % y_tile
        for x in range(x_tile // 8, 1 + (x_tile // 4) + (x_tile // 8)):
            x_conj = x_tile - x
            for j in range(y_blk):
                for i in range(x_blk):
                    out_data[j, y_conj, i, x_conj] = out_data[j, y, i, x].conjugate()
