#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.pal.transform
import pyctools.components.qt.qtdisplay
import pyctools.components.deinterlace.halfsize
import pyctools.components.fft.window
import pyctools.components.arithmetic
import pyctools.components.fft.fft
import pyctools.components.io.dumpmetadata
import pyctools.components.subtracter
import pyctools.components.fft.tile
import pyctools.components.pal.common
import pyctools.components.plumbing.busbar
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.modulate.modulate
import pyctools.components.io.videofilereader
import pyctools.components.pal.decoder

class Network(object):
    def __init__(self):
        self.components = \
{   'C': {   'class': 'pyctools.components.plumbing.busbar.Busbar',
             'config': '{}',
             'pos': (1700.0, 0.0)},
    'PAL': {   'class': 'pyctools.components.plumbing.busbar.Busbar',
               'config': '{}',
               'pos': (250.0, 0.0)},
    'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': '{}',
                 'pos': (2550.0, -150.0)},
    'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': '{}',
                       'pos': (350.0, 150.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': '{}',
                 'pos': (1950.0, 0.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'stats': 'on'}",
                   'pos': (2700.0, -150.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': "{'ytile': 16, 'xtile': 32}",
               'pos': (800.0, 150.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'path': '/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', '16bit': 'on', 'type': 'Y', 'looping': 'repeat'}",
                      'pos': (-50.0, 0.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'ytile': 16, 'xtile': 32, 'mode': 'thresh', 'threshold': 0.7}",
                    'pos': (950.0, 150.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'ytile': 16, 'xtile': 32, 'inverse': 'on', 'output': 'real'}",
                'pos': (1100.0, 150.0)},
    'inv_win_func': {   'class': 'pyctools.components.fft.window.InverseWindow',
                        'config': "{'ytile': 16, 'xtile': 32, 'xoff': 16, 'yoff': 8, 'fade': 'minsnr'}",
                        'pos': (500.0, 300.0)},
    'invwindow': {   'class': 'pyctools.components.modulate.modulate.Modulate',
                     'config': '{}',
                     'pos': (1250.0, 150.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.FromPAL',
                  'config': '{}',
                  'pos': (1800.0, 0.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': '{}',
                      'pos': (2100.0, 0.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'inverse': 'on'}",
                       'pos': (1550.0, 150.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'xdown': 461, 'xup': 351}",
                    'pos': (2400.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'outframe_pool_len': 12, 'func': '((data - 64.0) * (219.0 / 140.0)) + 16.0'}",
                    'pos': (100.0, 0.0)},
    'subtract': {   'class': 'pyctools.components.subtracter.Subtracter',
                    'config': '{}',
                    'pos': (1800.0, -150.0)},
    'tile': {   'class': 'pyctools.components.fft.tile.Tile',
                'config': "{'ytile': 16, 'xtile': 32, 'xoff': 16, 'yoff': 8}",
                'pos': (500.0, 150.0)},
    'untile': {   'class': 'pyctools.components.fft.tile.UnTile',
                  'config': '{}',
                  'pos': (1400.0, 150.0)},
    'win_func': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'ytile': 16, 'xtile': 32, 'alpha': 0.9}",
                    'pos': (350.0, 300.0)},
    'window': {   'class': 'pyctools.components.modulate.modulate.Modulate',
                  'config': '{}',
                  'pos': (650.0, 150.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'matrix': '601'}",
                    'pos': (2250.0, -150.0)}}
        self.linkages = \
{   ('C', 'output0'): ('subtract', 'input1'),
    ('C', 'output1'): ('matrix', 'input'),
    ('PAL', 'output0'): ('subtract', 'input0'),
    ('PAL', 'output1'): ('deinterlace', 'input'),
    ('audit', 'output'): ('display', 'input'),
    ('deinterlace', 'output'): ('tile', 'input'),
    ('demod', 'output'): ('postfilter', 'input'),
    ('fft', 'output'): ('filterUV', 'input'),
    ('filereader', 'output'): ('setlevel', 'input'),
    ('filterUV', 'output'): ('ifft', 'input'),
    ('ifft', 'output'): ('invwindow', 'input'),
    ('inv_win_func', 'inv_window'): ('invwindow', 'cell'),
    ('inv_win_func', 'window'): ('window', 'cell'),
    ('invwindow', 'output'): ('untile', 'input'),
    ('matrix', 'output'): ('demod', 'input'),
    ('postfilter', 'output'): ('yuvtorgb', 'input_UV'),
    ('reinterlace', 'output'): ('C', 'input'),
    ('resample', 'output'): ('audit', 'input'),
    ('setlevel', 'output'): ('PAL', 'input'),
    ('subtract', 'output'): ('yuvtorgb', 'input_Y'),
    ('tile', 'output'): ('window', 'input'),
    ('untile', 'output'): ('reinterlace', 'input'),
    ('win_func', 'output'): ('inv_win_func', 'input'),
    ('window', 'output'): ('fft', 'input'),
    ('yuvtorgb', 'output'): ('resample', 'input')}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])()
            cnf = comps[name].get_config()
            for key, value in eval(component['config']).items():
                cnf[key] = value
            comps[name].set_config(cnf)
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt4 import QtGui
    from PyQt4.QtCore import Qt
    QtGui.QApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QtGui.QApplication([])

    logging.basicConfig(level=logging.DEBUG)
    comp = Network().make()
    cnf = comp.get_config()
    parser = argparse.ArgumentParser()
    cnf.parser_add(parser)
    args = parser.parse_args()
    cnf.parser_set(args)
    comp.set_config(cnf)
    comp.start()
    app.exec_()
    comp.stop()
    comp.join()
