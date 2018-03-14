#!/usr/bin/env python
# File written by pyctools-editor. Do not edit.

import argparse
import logging
from pyctools.core.compound import Compound
import pyctools.components.modulate
import pyctools.components.pal.common
import pyctools.components.fft.fft
import pyctools.components.arithmetic
import pyctools.components.qt.qtdisplay
import pyctools.components.pal.decoder
import pyctools.components.colourspace.yuvtorgb
import pyctools.components.subtracter
import pyctools.components.pal.transform
import pyctools.components.fft.window
import pyctools.components.io.dumpmetadata
import pyctools.components.fft.tile
import pyctools.components.deinterlace.halfsize
import pyctools.components.io.videofilereader

class Network(object):
    components = \
{   'audit': {   'class': 'pyctools.components.io.dumpmetadata.DumpMetadata',
                 'config': "{'raw': 0, 'outframe_pool_len': 3}",
                 'pos': (2060.0, -40.0)},
    'deinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'topfirst': 1, 'inverse': 0, "
                                 "'outframe_pool_len': 3}",
                       'pos': (350.0, -40.0)},
    'demod': {   'class': 'pyctools.components.pal.common.ModulateUV',
                 'config': "{'outframe_pool_len': 3}",
                 'pos': (1560.0, -40.0)},
    'display': {   'class': 'pyctools.components.qt.qtdisplay.QtDisplay',
                   'config': "{'stats': 1, 'title': '', 'sync': 1, "
                             "'repeat': 1, 'shrink': 1, 'framerate': 25, "
                             "'expand': 1, 'outframe_pool_len': 3}",
                   'pos': (2060.0, -150.0)},
    'fft': {   'class': 'pyctools.components.fft.fft.FFT',
               'config': "{'xtile': 32, 'output': 'complex', 'inverse': 0, "
                         "'ytile': 16, 'outframe_pool_len': 3}",
               'pos': (710.0, -40.0)},
    'filereader': {   'class': 'pyctools.components.io.videofilereader.VideoFileReader',
                      'config': "{'16bit': 1, 'path': "
                                "'/home/jim/Documents/projects/pyctools-pal/coded_pal.avi', "
                                "'type': 'Y', 'looping': 'repeat', "
                                "'outframe_pool_len': 3}",
                      'pos': (100.0, -150.0)},
    'filterUV': {   'class': 'pyctools.components.pal.transform.FTFilterUV',
                    'config': "{'xtile': 32, 'mode': 'thresh', 'threshold': "
                              "0.7, 'ytile': 16, 'outframe_pool_len': 3}",
                    'pos': (830.0, -40.0)},
    'ifft': {   'class': 'pyctools.components.fft.fft.FFT',
                'config': "{'xtile': 32, 'output': 'real', 'inverse': 1, "
                          "'ytile': 16, 'outframe_pool_len': 3}",
                'pos': (950.0, -40.0)},
    'inv_win_func': {   'class': 'pyctools.components.fft.window.InverseWindow',
                        'config': "{'xtile': 32, 'xoff': 16, 'fade': "
                                  "'minsnr', 'ytile': 16, 'yoff': 8}",
                        'pos': (950.0, 70.0)},
    'invwindow': {   'class': 'pyctools.components.modulate.Modulate',
                     'config': "{'outframe_pool_len': 3}",
                     'pos': (1070.0, -40.0)},
    'matrix': {   'class': 'pyctools.components.pal.decoder.CtoUV',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (1440.0, -40.0)},
    'postfilter': {   'class': 'pyctools.components.pal.transform.PostFilterUV',
                      'config': "{'yup': 1, 'ydown': 1, 'xup': 1, 'xdown': "
                                "1, 'outframe_pool_len': 3}",
                      'pos': (1680.0, -40.0)},
    'reinterlace': {   'class': 'pyctools.components.deinterlace.halfsize.HalfSize',
                       'config': "{'topfirst': 1, 'inverse': 1, "
                                 "'outframe_pool_len': 3}",
                       'pos': (1310.0, -40.0)},
    'resample': {   'class': 'pyctools.components.pal.common.From4Fsc',
                    'config': "{'yup': 1, 'ydown': 1, 'xup': 351, 'xdown': "
                              "461, 'outframe_pool_len': 3}",
                    'pos': (1930.0, -150.0)},
    'setlevel': {   'class': 'pyctools.components.arithmetic.Arithmetic',
                    'config': "{'func': '((data - 64.0) * (219.0 / 140.0)) "
                              "+ 16.0', 'outframe_pool_len': 12}",
                    'pos': (220.0, -150.0)},
    'subtract': {   'class': 'pyctools.components.subtracter.Subtracter',
                    'config': "{'outframe_pool_len': 3}",
                    'pos': (1440.0, -150.0)},
    'tile': {   'class': 'pyctools.components.fft.tile.Tile',
                'config': "{'xtile': 32, 'xoff': 16, 'ytile': 16, 'yoff': "
                          "8, 'outframe_pool_len': 3}",
                'pos': (470.0, -40.0)},
    'untile': {   'class': 'pyctools.components.fft.tile.UnTile',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (1190.0, -40.0)},
    'win_func': {   'class': 'pyctools.components.fft.window.Kaiser',
                    'config': "{'xtile': 32, 'ytile': 16, 'alpha': 0.9}",
                    'pos': (470.0, 70.0)},
    'window': {   'class': 'pyctools.components.modulate.Modulate',
                  'config': "{'outframe_pool_len': 3}",
                  'pos': (590.0, -40.0)},
    'yuvtorgb': {   'class': 'pyctools.components.colourspace.yuvtorgb.YUVtoRGB',
                    'config': "{'range': 'studio', 'matrix': '601', "
                              "'outframe_pool_len': 3}",
                    'pos': (1810.0, -150.0)}}
    linkages = \
{   ('deinterlace', 'output'): [('tile', 'input')],
    ('demod', 'output'): [('postfilter', 'input')],
    ('fft', 'output'): [('filterUV', 'input')],
    ('filereader', 'output'): [('setlevel', 'input')],
    ('filterUV', 'output'): [('ifft', 'input')],
    ('ifft', 'output'): [('invwindow', 'input')],
    ('inv_win_func', 'inv_window'): [('invwindow', 'cell')],
    ('invwindow', 'output'): [('untile', 'input')],
    ('matrix', 'output'): [('demod', 'input')],
    ('postfilter', 'output'): [('yuvtorgb', 'input_UV')],
    ('reinterlace', 'output'): [('matrix', 'input'), ('subtract', 'input1')],
    ('resample', 'output'): [('audit', 'input'), ('display', 'input')],
    ('setlevel', 'output'): [('subtract', 'input0'), ('deinterlace', 'input')],
    ('subtract', 'output'): [('yuvtorgb', 'input_Y')],
    ('tile', 'output'): [('window', 'input')],
    ('untile', 'output'): [('reinterlace', 'input')],
    ('win_func', 'output'): [('window', 'cell'), ('inv_win_func', 'input')],
    ('window', 'output'): [('fft', 'input')],
    ('yuvtorgb', 'output'): [('resample', 'input')]}

    def make(self):
        comps = {}
        for name, component in self.components.items():
            comps[name] = eval(component['class'])(config=eval(component['config']))
        return Compound(linkages=self.linkages, **comps)

if __name__ == '__main__':
    from PyQt5 import QtCore, QtWidgets
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QtWidgets.QApplication([])

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
