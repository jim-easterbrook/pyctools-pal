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
import pyctools.components.fft.fft
import pyctools.components.fft.tile
import pyctools.components.fft.window
import pyctools.components.io.dumpmetadata
import pyctools.components.io.videofilereader
import pyctools.components.modulate
import pyctools.components.pal.common
import pyctools.components.pal.decoder
import pyctools.components.pal.transform
import pyctools.components.qt.qtdisplay

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (2540.0, -40.0)},
    'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': '{}',
                       'pos': (350.0, -40.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': '{}',
                 'pos': (2040.0, -40.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'stats': True}",
                   'pos': (2540.0, -150.0)},
    'fftX': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'xtile': 32, 'ytile': 1, 'submean': True}",
                'pos': (110.0, -40.0)},
    'fftY': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'xtile': 1, 'ytile': 16}",
                'pos': (710.0, -40.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': "
                                "'/home/jim/Documents/projects/pyctools/pyctools-pal/BBC_pal/JEE_mobcal_pal.avi', "
                                "'looping': 'repeat', 'type': 'Y', '16bit': "
                                "True, 'noaudit': True, 'zperiod': 4}",
                      'pos': (-380.0, -150.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'xtile': 32, 'ytile': 16, 'mode': 'thresh', "
                              "'threshold': 0.7}",
                    'pos': (830.0, -40.0)},
    'ifftX': {   'class': 'pyctools.components.fft.fft.FFT',
                 'config': "{'xtile': 32, 'ytile': 1, 'inverse': True, "
                           "'output': 'real'}",
                 'pos': (1550.0, -40.0)},
    'ifftY': {   'class': 'pyctools.components.fft.fft.FFT',
                 'config': "{'xtile': 1, 'ytile': 16, 'inverse': True}",
                 'pos': (950.0, -40.0)},
    'invwindowX': {   'class': 'pyctools.components.modulate.Modulate',
                      'config': '{}',
                      'pos': (1670.0, -40.0)},
    'invwindowY': {   'class': 'pyctools.components.modulate.Modulate',
                      'config': '{}',
                      'pos': (1070.0, -40.0)},
    'invwinfuncX': {   'class': 'pyctools.components.fft.window.InverseWindow',
                       'config': "{'xtile': 32, 'xoff': 16, 'fade': 'minsnr'}",
                       'pos': (1550.0, 120.0)},
    'invwinfuncY': {   'class': 'pyctools.components.fft.window.InverseWindow',
                       'config': "{'ytile': 16, 'yoff': 8, 'fade': 'minsnr'}",
                       'pos': (950.0, 70.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.CtoUV',
                  'config': '{}',
                  'pos': (1920.0, -40.0)},
    'pad': {   'class': 'pyctools.components.pal.transform.HorizontalSubset',
               'config': "{'xtile': 32, 'inverse': True}",
               'pos': (1430.0, -40.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': '{}',
                      'pos': (2160.0, -40.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'inverse': True}",
                       'pos': (1310.0, -40.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'resize': {'xup': 351, 'xdown': 461}, "
                              "'filgen': {'xup': 351, 'xdown': 461, "
                              "'xaperture': 12}}",
                    'expanded': False,
                    'pos': (2410.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '(data - 64.0) * (255.0 / 140.0)', "
                              "'outframe_pool_len': 16}",
                    'pos': (-260.0, -150.0)},
    'subset': {   'class': 'pyctools.components.pal.transform.HorizontalSubset',
                  'config': "{'xtile': 32}",
                  'pos': (230.0, -40.0)},
    'subtract': {   'class': 'pyctools.components.arithmetic.Arithmetic2',
                    'config': "{'func': 'data1 - data2'}",
                    'pos': (1920.0, -150.0)},
    'tileX': {   'class': 'pyctools.components.fft.tile.Tile',
                 'config': "{'xtile': 32, 'xoff': 16}",
                 'pos': (-130.0, -40.0)},
    'tileY': {   'class': 'pyctools.components.fft.tile.Tile',
                 'config': "{'ytile': 16, 'yoff': 8}",
                 'pos': (470.0, -40.0)},
    'untileX': {   'class': 'pyctools.components.fft.tile.UnTile',
                   'config': '{}',
                   'pos': (1790.0, -40.0)},
    'untileY': {   'class': 'pyctools.components.fft.tile.UnTile',
                   'config': '{}',
                   'pos': (1190.0, -40.0)},
    'windowX': {   'class': 'pyctools.components.modulate.Modulate',
                   'config': '{}',
                   'pos': (-10.0, -40.0)},
    'windowY': {   'class': 'pyctools.components.modulate.Modulate',
                   'config': '{}',
                   'pos': (590.0, -40.0)},
    'winfuncX': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'xtile': 32}",
                    'pos': (-130.0, 120.0)},
    'winfuncY': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'ytile': 16}",
                    'pos': (470.0, 70.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'matrix': '601'}",
                    'pos': (2290.0, -150.0)}}
    linkages = \
{   ('deinterlace', 'output'): [('tileY', 'input')],
    ('demod', 'output'): [('postfilter', 'input')],
    ('fftX', 'output'): [('subset', 'input')],
    ('fftY', 'output'): [('filterUV', 'input')],
    ('filereader', 'output'): [('setlevel', 'input')],
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
    ('resample', 'output'): [('audit', 'input'), ('display', 'input')],
    ('setlevel', 'output'): [('subtract', 'input1'), ('tileX', 'input')],
    ('subset', 'output'): [('deinterlace', 'input')],
    ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
    ('tileX', 'output'): [('windowX', 'input')],
    ('tileY', 'output'): [('windowY', 'input')],
    ('untileX', 'output'): [('subtract', 'input2'), ('matrix', 'input')],
    ('untileY', 'output'): [('reinterlace', 'input')],
    ('windowX', 'output'): [('fftX', 'input')],
    ('windowY', 'output'): [('fftY', 'input')],
    ('winfuncX', 'output'): [('invwinfuncX', 'input'), ('windowX', 'cell')],
    ('winfuncY', 'output'): [('windowY', 'cell'), ('invwinfuncY', 'input')],
    ('yuvtorgb', 'output'): [('resample', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication(sys.argv)

    comp = Network().make()
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
