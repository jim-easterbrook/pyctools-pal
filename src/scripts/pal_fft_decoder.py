#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.fft.window
import pyctools.components.fft.tile
import pyctools.components.qt.qtdisplay
import pyctools.components.subtracter
import pyctools.components.deinterlace.halfsize
import pyctools.components.pal.common
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.fft.fft
import pyctools.components.modulate.modulate
import pyctools.components.pal.transform
import pyctools.components.arithmetic
import pyctools.components.io.videofilereader
import pyctools.components.pal.decoder
import pyctools.components.io.dumpmetadata

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (2450.0, 50.0)},
    'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'topfirst': 'on'}",
                       'pos': (350.0, 0.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': '{}',
                 'pos': (1850.0, 0.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'repeat': 'on', 'stats': 'on', 'sync': 'on'}",
                   'pos': (2450.0, -150.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': "{'ytile': 16, 'xtile': 32}",
               'pos': (800.0, 0.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', '16bit': 'on', 'type': 'Y', 'looping': 'repeat'}",
                      'pos': (50.0, -150.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'ytile': 16, 'xtile': 32, 'mode': 'thresh', 'threshold': 0.7}",
                    'pos': (950.0, 0.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'ytile': 16, 'xtile': 32, 'inverse': 'on', 'output': 'real'}",
                'pos': (1100.0, 0.0)},
    'inv_win_func': {   'class': 'pyctools.components.fft.window.InverseWindow',
                        'config': "{'ytile': 16, 'xtile': 32, 'xoff': 16, 'yoff': 8, 'fade': 'minsnr'}",
                        'pos': (500.0, 150.0)},
    'invwindow': {   'class': 'pyctools.components.modulate.modulate.Modulate',
                     'config': '{}',
                     'pos': (1250.0, 0.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': '{}',
                  'pos': (1700.0, 0.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': '{}',
                      'pos': (2000.0, 0.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'inverse': 'on', 'topfirst': 'on'}",
                       'pos': (1550.0, 0.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'xup': 351}",
                    'pos': (2300.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'outframe_pool_len': 12, 'func': '((data - 64.0) * (219.0 / 140.0)) + 16.0'}",
                    'pos': (200.0, -150.0)},
    'subtract': {   'class': 'pyctools.components.subtracter.Subtracter',
                    'config': '{}',
                    'pos': (1700.0, -150.0)},
    'tile': {   'class': 'pyctools.components.fft.tile.Tile',
                'config': "{'ytile': 16, 'xtile': 32, 'xoff': 16, 'yoff': 8}",
                'pos': (500.0, 0.0)},
    'untile': {   'class': 'pyctools.components.fft.tile.UnTile',
                  'config': '{}',
                  'pos': (1400.0, 0.0)},
    'win_func': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'ytile': 16, 'xtile': 32, 'alpha': 0.9}",
                    'pos': (350.0, 150.0)},
    'window': {   'class': 'pyctools.components.modulate.modulate.Modulate',
                  'config': '{}',
                  'pos': (650.0, 0.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'matrix': '601'}",
                    'pos': (2150.0, -150.0)}}
    linkages = \
{   ('deinterlace', 'output'): [('tile', 'input')],
    ('demod', 'output'): [('postfilter', 'input')],
    ('fft', 'output'): [('filterUV', 'input')],
    ('filereader', 'output'): [('setlevel', 'input')],
    ('filterUV', 'output'): [('ifft', 'input')],
    ('ifft', 'output'): [('invwindow', 'input')],
    ('inv_win_func', 'inv_window'): [('invwindow', 'cell')],
    ('inv_win_func', 'window'): [('window', 'cell')],
    ('invwindow', 'output'): [('untile', 'input')],
    ('matrix', 'output'): [('demod', 'input')],
    ('postfilter', 'output'): [('yuvtorgb', 'input_UV')],
    ('reinterlace', 'output'): [('subtract', 'input1'), ('matrix', 'input')],
    ('resample', 'output'): [('display', 'input'), ('audit', 'input')],
    ('setlevel', 'output'): [('deinterlace', 'input'), ('subtract', 'input0')],
    ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
    ('tile', 'output'): [('window', 'input')],
    ('untile', 'output'): [('reinterlace', 'input')],
    ('win_func', 'output'): [('inv_win_func', 'input')],
    ('window', 'output'): [('fft', 'input')],
    ('yuvtorgb', 'output'): [('resample', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(**eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt4 import QtGui
    from PyQt4.QtCore import Qt
    QtGui.QApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QtGui.QApplication([])

    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser()
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
