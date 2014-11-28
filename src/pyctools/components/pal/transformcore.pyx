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
        unsigned int i, j, x, y, x_conj, y_conj, x_ref, y_ref, x_ref_conj, y_ref_conj
        CMPLX_t in_val, ref_val, out_val, out_ref
        FLOAT_t m_in, m_ref, gain
    y_blk = out_data.shape[0]
    y_tile = out_data.shape[1]
    x_blk = out_data.shape[2]
    x_tile = out_data.shape[3]
    for x in range(x_tile // 8, 1 + (x_tile // 4)):
        x_conj = x_tile - x
        x_ref = (x_tile // 2) - x
        x_ref_conj = x_tile - x_ref
        for y in range(y_tile):
            y_conj = (y_tile - y) % y_tile
            y_ref = ((y_tile // 2) + y_tile - y) % y_tile
            y_ref_conj = (y_tile - y_ref) % y_tile
            for j in range(y_blk):
                for i in range(x_blk):
                    in_val = in_data[j, y, i, x]
                    ref_val = in_data[j, y_ref, i, x_ref]
                    m_in = abs(in_val)
                    m_ref = abs(ref_val)
                    if threshold == 0.0:
                        if m_in < m_ref:
                            out_val = in_val
                            out_ref = ref_val * m_in / m_ref
                        else:
                            out_val = in_val * m_ref / m_in
                            out_ref = ref_val
                    else:
                        if (m_in < m_ref * threshold or
                                m_ref < m_in * threshold):
                            continue
                        else:
                            out_val = in_val
                            out_ref = ref_val
                    out_data[j, y, i, x] = out_val
                    out_data[j, y_conj, i, x_conj] = out_val.conjugate()
                    out_data[j, y_ref, i, x_ref] = out_ref
                    out_data[j, y_ref_conj, i, x_ref_conj] = out_ref.conjugate()
