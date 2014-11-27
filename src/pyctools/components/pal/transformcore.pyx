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

cimport cython
cimport numpy

ctypedef numpy.complex64_t CMPLX_t
ctypedef numpy.float32_t FLOAT_t

def transform_filter(numpy.ndarray[CMPLX_t, ndim=4] out_data,
                     numpy.ndarray[CMPLX_t, ndim=4] in_data,
                     FLOAT_t threshold):
    cdef:
        unsigned int x_blk, y_blk, x_tile, y_tile
        unsigned int i, j, x, y, x_conj, y_conj, x_ref, y_ref
        float x_f
        CMPLX_t in_val, ref_val, out_val
        FLOAT_t m_in, m_ref
    y_blk = out_data.shape[0]
    y_tile = out_data.shape[1]
    x_blk = out_data.shape[2]
    x_tile = out_data.shape[3]
    out_data[:, :, :, 0] = 0.0
    out_data[:, :, :, x_tile // 2] = 0.0
    for x in range(1, x_tile // 2):
        x_conj = x_tile - x
        # normalised horizontal frequency distance from fsc
        x_f = (<float>x / <float>x_tile) - 0.25
        if abs(x_f) >= 0.125:
            out_data[:, :, :, x] = 0.0
            out_data[:, :, :, x_conj] = 0.0
        else:
            x_ref = (x_tile // 2) - x
            for j in range(y_blk):
                for y in range(y_tile):
                    y_conj = (y_tile - y) % y_tile
                    y_ref = ((y_tile // 2) + y_tile - y) % y_tile
                    for i in range(x_blk):
                        in_val = in_data[j, y, i, x]
                        ref_val = in_data[j, y_ref, i, x_ref]
                        m_in = abs(in_val)
                        m_ref = abs(ref_val)
                        if threshold == 0.0:
                            if m_in < m_ref:
                                out_val = in_val
                            else:
                                out_val = in_val * m_ref / m_in
                        else:
                            if (m_in < m_ref * threshold or
                                    m_ref < m_in * threshold):
                                out_val = 0.0
                            else:
                                out_val = in_val
                        out_data[j, y, i, x] = out_val
                        out_data[j, y_conj, i, x_conj] = out_val.conjugate()
