#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
import sys

from PyQt5 import QtCore, QtWidgets

from pyctools.core.compound import Compound
import pyctools.components.arithmetic
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.deinterlace.halfsize
import pyctools.components.deinterlace.weston3field
import pyctools.components.fft.fft
import pyctools.components.fft.tile
import pyctools.components.fft.window
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader2
import pyctools.components.modulate
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.pal.transform
import pyctools.components.qt.qtdisplay

class ComponentNetwork(Compound):
    positions = {'audit': (1220.0, -40.0),
                 'deint': (1220.0, -160.0),
                 'deinterlace': (-10.0, 190.0),
                 'demod': (840.0, -40.0),
                 'display': (1340.0, -160.0),
                 'fftX': (110.0, -40.0),
                 'fftY': (110.0, 310.0),
                 'filereader': (-130.0, -160.0),
                 'filterUV': (230.0, 310.0),
                 'ifftX': (350.0, -40.0),
                 'ifftY': (350.0, 310.0),
                 'invwindowX': (470.0, -40.0),
                 'invwindowY': (470.0, 310.0),
                 'invwinfuncX': (350.0, 70.0),
                 'invwinfuncY': (350.0, 420.0),
                 'matrix': (720.0, -40.0),
                 'pad': (590.0, 190.0),
                 'postfilter': (960.0, -40.0),
                 'reinterlace': (470.0, 190.0),
                 'resample': (1090.0, -160.0),
                 'setlevel': (-10.0, -160.0),
                 'subset': (-130.0, 190.0),
                 'subtract': (720.0, -160.0),
                 'tileX': (-130.0, -40.0),
                 'tileY': (-130.0, 310.0),
                 'untileX': (590.0, -40.0),
                 'untileY': (590.0, 310.0),
                 'windowX': (-10.0, -40.0),
                 'windowY': (-10.0, 310.0),
                 'winfuncX': (-130.0, 70.0),
                 'winfuncY': (-130.0, 420.0),
                 'yuvtorgb': (960.0, -160.0)}
    expanded = {'resample': False}
    user_config = {
        'display': {'framerate': 50, 'stats': True, 'title': 'Transform PAL'},
        'fftX': {'submean': True, 'xtile': 32, 'ytile': 1},
        'fftY': {'xtile': 1, 'ytile': 16},
        'filterUV': {'mode': 'thresh',
                     'threshold': 0.7,
                     'xtile': 32,
                     'ytile': 16},
        'ifftX': {'inverse': True, 'output': 'real', 'xtile': 32, 'ytile': 1},
        'ifftY': {'inverse': True, 'xtile': 1, 'ytile': 16},
        'invwinfuncX': {'fade': 'minsnr', 'xoff': 16, 'xtile': 32},
        'invwinfuncY': {'fade': 'minsnr', 'yoff': 8, 'ytile': 16},
        'pad': {'inverse': True, 'xtile': 32},
        'reinterlace': {'inverse': True},
        'setlevel': {'func': '(data - 64.0) * (255.0 / 140.0)',
                     'outframe_pool_len': 16},
        'subset': {'xtile': 32},
        'subtract': {'func': 'data1 - data2'},
        'tileX': {'xoff': 16, 'xtile': 32},
        'tileY': {'yoff': 8, 'ytile': 16},
        'winfuncX': {'xtile': 32},
        'winfuncY': {'ytile': 16},
        'yuvtorgb': {'matrix': '601'},
        'filereader': {'format': 'Y',
                       'looping': 'repeat',
                       'noaudit': True,
                       'path': '/home/jim/Documents/projects/pyctools/pyctools-pal/coded_pal.y16',
                       'zperiod': 4},
        }


    def __init__(self):
        super(ComponentNetwork, self).__init__(
            audit = pyctools.components.io.dumpmetadata.DumpMetadata(),
            deint = pyctools.components.deinterlace.weston3field.Weston3Field(),
            deinterlace = pyctools.components.deinterlace.halfsize.HalfSize(),
            demod = pyctools.components.pal.common.ModulateUV(),
            display = pyctools.components.qt.qtdisplay.QtDisplay(),
            fftX = pyctools.components.fft.fft.FFT(),
            fftY = pyctools.components.fft.fft.FFT(),
            filterUV = pyctools.components.pal.transform.FTFilterUV(),
            ifftX = pyctools.components.fft.fft.FFT(),
            ifftY = pyctools.components.fft.fft.FFT(),
            invwindowX = pyctools.components.modulate.Modulate(),
            invwindowY = pyctools.components.modulate.Modulate(),
            invwinfuncX = pyctools.components.fft.window.InverseWindow(),
            invwinfuncY = pyctools.components.fft.window.InverseWindow(),
            matrix = pyctools.components.pal.decoder.CtoUV(),
            pad = pyctools.components.pal.transform.HorizontalSubset(),
            postfilter = pyctools.components.pal.transform.PostFilterUV(),
            reinterlace = pyctools.components.deinterlace.halfsize.HalfSize(),
            resample = pyctools.components.pal.common.From4Fsc(),
            setlevel = pyctools.components.arithmetic.Arithmetic(),
            subset = pyctools.components.pal.transform.HorizontalSubset(),
            subtract = pyctools.components.arithmetic.Arithmetic2(),
            tileX = pyctools.components.fft.tile.Tile(),
            tileY = pyctools.components.fft.tile.Tile(),
            untileX = pyctools.components.fft.tile.UnTile(),
            untileY = pyctools.components.fft.tile.UnTile(),
            windowX = pyctools.components.modulate.Modulate(),
            windowY = pyctools.components.modulate.Modulate(),
            winfuncX = pyctools.components.fft.window.Kaiser(),
            winfuncY = pyctools.components.fft.window.Kaiser(),
            yuvtorgb = pyctools.components.colourspace.yuvtorgb.YUVtoRGB(),
            filereader = pyctools.components.io.videofilereader2.VideoFileReader2(),
            linkages = {('deint', 'output'): [('display', 'input')],
                        ('deinterlace', 'output'): [('tileY', 'input')],
                        ('demod', 'output'): [('postfilter', 'input')],
                        ('fftX', 'output'): [('subset', 'input')],
                        ('fftY', 'output'): [('filterUV', 'input')],
                        ('filereader', 'output_Y_RGB'): [('setlevel', 'input')],
                        ('filterUV', 'output'): [('ifftY', 'input')],
                        ('ifftX', 'output'): [('invwindowX', 'input')],
                        ('ifftY', 'output'): [('invwindowY', 'input')],
                        ('invwindowX', 'output'): [('untileX', 'input')],
                        ('invwindowY', 'output'): [('untileY', 'input')],
                        ('invwinfuncX', 'inv_window'): [('invwindowX', 'cell')],
                        ('invwinfuncY', 'inv_window'): [('invwindowY', 'cell')],
                        ('matrix', 'output'): [('demod', 'input')],
                        ('pad', 'output'): [('ifftX', 'input')],
                        ('postfilter', 'output'): [('yuvtorgb', 'input_UV')],
                        ('reinterlace', 'output'): [('pad', 'input')],
                        ('resample', 'output'): [('deint', 'input'),
                                                 ('audit', 'input')],
                        ('setlevel', 'output'): [('tileX', 'input'),
                                                 ('subtract', 'input1')],
                        ('subset', 'output'): [('deinterlace', 'input')],
                        ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
                        ('tileX', 'output'): [('windowX', 'input')],
                        ('tileY', 'output'): [('windowY', 'input')],
                        ('untileX', 'output'): [('matrix', 'input'),
                                                ('subtract', 'input2')],
                        ('untileY', 'output'): [('reinterlace', 'input')],
                        ('windowX', 'output'): [('fftX', 'input')],
                        ('windowY', 'output'): [('fftY', 'input')],
                        ('winfuncX', 'output'): [('windowX', 'cell'),
                                                 ('invwinfuncX', 'input')],
                        ('winfuncY', 'output'): [('invwinfuncY', 'input'),
                                                 ('windowY', 'cell')],
                        ('yuvtorgb', 'output'): [('resample', 'input')]}
            )

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

    comp = ComponentNetwork()
    comp.set_config(comp.user_config)
    cnf = comp.get_config()
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    cnf.parser_add(parser)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='increase verbosity of log messages')
    args = parser.parse_args()
    logging.basicConfig(level=logging.ERROR - (args.verbose * 10))
    del args.verbose
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()
    app.exec_()

    comp.stop()
    comp.join()
